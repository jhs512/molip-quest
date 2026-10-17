//! Neural Korean speech for 해설 모드: the voices of Microsoft Edge's "소리 내어 읽기" (선히, 인준,
//! 현수), fetched with the installed edge-tts client. Its 7.3.1 release tracks the newer
//! service handshake; the legacy built-in client remains a secondary option. The learning
//! installer supplies the Python package, and diagnostics check both its version and the
//! actual online connection separately. The page asks for audio over the app's custom
//! protocol (`molip://localhost/tts`, `http://molip.localhost/tts` on Windows) and plays the MP3;
//! with no network at all it falls back to the system voice. Clips are cached under the app data
//! folder, so a sentence is synthesized once.

use std::path::PathBuf;

/// Voices the settings offer; the first is the default.
pub const VOICES: [(&str, &str); 4] = [
    ("ko-KR-SunHiNeural", "선히 · 여성, 자연스러운 음성 (인터넷 필요)"),
    ("ko-KR-InJoonNeural", "인준 · 남성, 자연스러운 음성 (인터넷 필요)"),
    ("ko-KR-HyunsuMultilingualNeural", "현수 · 남성, 다국어 음성 (인터넷 필요)"),
    ("system", "기기 기본 음성 · 오프라인"),
];

pub fn default_voice() -> String {
    VOICES[0].0.to_string()
}

fn is_known_voice(voice: &str) -> bool {
    VOICES.iter().any(|(id, _)| *id == voice && *id != "system")
}

// ---- Legacy Edge Read Aloud protocol (edge-tts 7.2.8); try the updated Python client first. ----
const TRUSTED_CLIENT_TOKEN: &str = "6A5AA1D4EAFF4E9FB37E23D68491D6F4";
const CHROMIUM_FULL_VERSION: &str = "143.0.3650.75";
const CHROMIUM_MAJOR_VERSION: &str = "143";
const WSS_URL: &str =
    "wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1";
const WIN_EPOCH: f64 = 11644473600.0;

fn sha256_hex_upper(input: &str) -> String {
    use sha2::{Digest, Sha256};
    let digest = Sha256::digest(input.as_bytes());
    digest.iter().map(|b| format!("{b:02X}")).collect()
}

/// The `Sec-MS-GEC` value: SHA-256 of the Windows file time (100 ns ticks since 1601), rounded
/// down to five minutes, followed by the trusted client token; upper-case hex.
pub fn drm_token(unix_seconds: f64) -> String {
    let mut ticks = unix_seconds + WIN_EPOCH;
    ticks -= ticks % 300.0;
    ticks *= 1e9 / 100.0;
    sha256_hex_upper(&format!("{ticks:.0}{TRUSTED_CLIENT_TOKEN}"))
}

/// JavaScript's `Date.toString()` in UTC, which the service expects in X-Timestamp.
pub fn js_date_string(unix_seconds: u64) -> String {
    const DAYS: [&str; 7] = ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"]; // 1970-01-01 was a Thursday
    const MONTHS: [&str; 12] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    let days = unix_seconds / 86400;
    let secs = unix_seconds % 86400;
    // Civil-from-days (Howard Hinnant's algorithm).
    let z = days as i64 + 719468;
    let era = z.div_euclid(146097);
    let doe = z.rem_euclid(146097);
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };
    format!(
        "{} {} {:02} {} {:02}:{:02}:{:02} GMT+0000 (Coordinated Universal Time)",
        DAYS[(days % 7) as usize],
        MONTHS[(m - 1) as usize],
        d,
        y,
        secs / 3600,
        secs % 3600 / 60,
        secs % 60
    )
}

fn now_unix() -> f64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

/// 32 hex characters, fresh per connection and request.
fn connection_id() -> String {
    use std::sync::atomic::{AtomicU64, Ordering};
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    let n = COUNTER.fetch_add(1, Ordering::Relaxed);
    let seed = format!("{}-{}-{}", now_unix(), n, std::process::id());
    sha256_hex_upper(&seed)[..32].to_lowercase()
}

fn escape_xml(text: &str) -> String {
    text.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")
}

pub fn ssml(voice: &str, text: &str) -> String {
    format!(
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'><voice name='{voice}'><prosody pitch='+0Hz' rate='+0%' volume='+0%'>{}</prosody></voice></speak>",
        escape_xml(text)
    )
}

/// Audio from the service itself: connect, send the config and the SSML, collect the `audio`
/// binary frames until `turn.end`.
#[cfg(not(target_os = "android"))]
fn edge_native(voice: &str, text: &str) -> Result<Vec<u8>, String> {
    use std::net::ToSocketAddrs;
    use tungstenite::client::IntoClientRequest;
    use tungstenite::Message;
    let url = format!(
        "{WSS_URL}?TrustedClientToken={TRUSTED_CLIENT_TOKEN}&ConnectionId={}&Sec-MS-GEC={}&Sec-MS-GEC-Version=1-{CHROMIUM_FULL_VERSION}",
        connection_id(),
        drm_token(now_unix())
    );
    let mut request = url
        .into_client_request()
        .map_err(|e| format!("음성 서버 주소 오류: {e}"))?;
    let headers = request.headers_mut();
    let header = |value: &str| value.parse().expect("ascii header value");
    headers.insert("Pragma", header("no-cache"));
    headers.insert("Cache-Control", header("no-cache"));
    headers.insert("Origin", header("chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold"));
    headers.insert("User-Agent", header(&format!("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROMIUM_MAJOR_VERSION}.0.0.0 Safari/537.36 Edg/{CHROMIUM_MAJOR_VERSION}.0.0.0")));
    headers.insert("Accept-Encoding", header("gzip, deflate, br, zstd"));
    headers.insert("Accept-Language", header("en-US,en;q=0.9"));
    headers.insert("Cookie", header(&format!("muid={};", connection_id().to_uppercase())));
    // A blocked or absent network must fail in seconds, not hang the narration: connect with a
    // timeout and give the socket read/write deadlines before the TLS handshake.
    let stream = std::net::TcpStream::connect_timeout(
        &("speech.platform.bing.com", 443)
            .to_socket_addrs()
            .map_err(|e| format!("음성 서버 주소를 찾지 못했습니다: {e}"))?
            .next()
            .ok_or("음성 서버 주소를 찾지 못했습니다.")?,
        std::time::Duration::from_secs(6),
    )
    .map_err(|e| format!("음성 서버 연결 실패: {e}"))?;
    stream.set_read_timeout(Some(std::time::Duration::from_secs(15))).map_err(|e| e.to_string())?;
    stream.set_write_timeout(Some(std::time::Duration::from_secs(15))).map_err(|e| e.to_string())?;
    let (mut socket, _response) = tungstenite::client_tls(request, stream).map_err(|e| format!("음성 서버 연결 실패: {e}"))?;
    let stamp = js_date_string(now_unix() as u64);
    socket
        .send(Message::text(format!(
            "X-Timestamp:{stamp}\r\nContent-Type:application/json; charset=utf-8\r\nPath:speech.config\r\n\r\n{{\"context\":{{\"synthesis\":{{\"audio\":{{\"metadataoptions\":{{\"sentenceBoundaryEnabled\":\"false\",\"wordBoundaryEnabled\":\"true\"}},\"outputFormat\":\"audio-24khz-48kbitrate-mono-mp3\"}}}}}}}}\r\n"
        )))
        .map_err(|e| format!("음성 설정 전송 실패: {e}"))?;
    socket
        .send(Message::text(format!(
            "X-RequestId:{}\r\nContent-Type:application/ssml+xml\r\nX-Timestamp:{stamp}Z\r\nPath:ssml\r\n\r\n{}",
            connection_id(),
            ssml(voice, text)
        )))
        .map_err(|e| format!("문장 전송 실패: {e}"))?;
    let mut audio = Vec::new();
    loop {
        let message = socket.read().map_err(|e| format!("음성 수신 실패: {e}"))?;
        match message {
            Message::Text(frame) => {
                let frame = frame.as_str();
                if frame.contains("Path:turn.end") {
                    break;
                }
            }
            Message::Binary(frame) => {
                if frame.len() < 2 {
                    continue;
                }
                let header_len = u16::from_be_bytes([frame[0], frame[1]]) as usize + 2;
                if header_len > frame.len() {
                    continue;
                }
                let header = String::from_utf8_lossy(&frame[2..header_len]);
                if header.contains("Path:audio") {
                    audio.extend_from_slice(&frame[header_len..]);
                }
            }
            Message::Close(_) => break,
            _ => {}
        }
    }
    let _ = socket.close(None);
    if audio.is_empty() {
        return Err("음성 서버가 소리를 보내지 않았습니다.".into());
    }
    Ok(audio)
}

#[cfg(target_os = "android")]
fn edge_native(_voice: &str, _text: &str) -> Result<Vec<u8>, String> {
    Err("Android 열람 모드에는 해설 음성이 없습니다.".into())
}

/// The installed edge-tts client tracks Microsoft's newer handshake without duplicating
/// that protocol here: https://github.com/rany2/edge-tts/tree/7.3.1
fn edge_python(voice: &str, text: &str, path: &std::path::Path) -> Result<Vec<u8>, String> {
    let mut command = std::process::Command::new(crate::runner::python_executable());
    command
        .args(["-I", "-X", "utf8", "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media"])
        .arg(path)
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::piped());
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    let mut child = command
        .spawn()
        .map_err(|e| format!("edge-tts를 실행하지 못했습니다: {e}"))?;
    let started = std::time::Instant::now();
    loop {
        if child.try_wait().map_err(|e| e.to_string())?.is_some() {
            break;
        }
        if started.elapsed() >= std::time::Duration::from_secs(15) {
            let _ = child.kill();
            let _ = child.wait();
            let _ = std::fs::remove_file(path);
            return Err("대체 음성 연결 시간이 초과됐어요. 기기 음성이나 자막으로 이어가요.".into());
        }
        std::thread::sleep(std::time::Duration::from_millis(25));
    }
    let output = child.wait_with_output().map_err(|e| e.to_string())?;
    if !output.status.success() {
        let _ = std::fs::remove_file(path);
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(python_failure(&stderr));
    }
    let bytes = std::fs::read(path).map_err(|e| e.to_string())?;
    if bytes.is_empty() {
        let _ = std::fs::remove_file(path);
        return Err("edge-tts가 빈 파일을 만들었습니다.".into());
    }
    Ok(bytes)
}

fn python_failure(stderr: &str) -> String {
    if stderr.contains("No module named edge_tts") || stderr.contains("No module named 'edge_tts'") {
        return "이 Python 환경에 edge-tts 음성 패키지가 없어요. 환경 설치(다시)를 눌러 추가하세요. 그동안 기기 음성이나 자막으로 이어가요.".into();
    }
    let reason = stderr.lines().rev().find(|l| !l.trim().is_empty()).unwrap_or("");
    format!("대체 음성 연결 실패: {reason}")
}

fn cache_path(voice: &str, text: &str) -> Result<PathBuf, String> {
    // A short, stable name per (voice, text): FNV-1a over both, hex.
    let mut hash: u64 = 0xcbf29ce484222325;
    for byte in voice.bytes().chain([0u8]).chain(text.bytes()) {
        hash ^= byte as u64;
        hash = hash.wrapping_mul(0x100000001b3);
    }
    let dir = crate::data_dir()?.join("tts-cache");
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir.join(format!("{voice}-{hash:016x}.mp3")))
}

/// MP3 bytes for the sentence and which engine produced them ("cache", "edge", "edge-tts").
pub fn synthesize(voice: &str, text: &str) -> Result<(Vec<u8>, &'static str), String> {
    let text = text.trim();
    if text.is_empty() || text.len() > 2000 {
        return Err("문장이 비었거나 너무 깁니다.".into());
    }
    if !is_known_voice(voice) {
        return Err(format!("모르는 음성입니다: {voice}"));
    }
    let path = cache_path(voice, text)?;
    if let Ok(bytes) = std::fs::read(&path) {
        if !bytes.is_empty() {
            return Ok((bytes, "cache"));
        }
    }
    let result = synthesize_from_clients(
        || edge_python(voice, text, &path),
        || edge_native(voice, text),
    )?;
    let _ = std::fs::write(&path, &result.0);
    Ok(result)
}

fn synthesize_from_clients(
    updated: impl FnOnce() -> Result<Vec<u8>, String>,
    legacy: impl FnOnce() -> Result<Vec<u8>, String>,
) -> Result<(Vec<u8>, &'static str), String> {
    match updated() {
        Ok(bytes) => Ok((bytes, "edge-tts")),
        Err(python_error) => match legacy() {
            Ok(bytes) => Ok((bytes, "edge")),
            Err(native_error) => Err(format!("{python_error} / 내장 음성 연결: {native_error}")),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn missing_voice_package_is_distinct_from_an_online_service_rejection() {
        let missing = python_failure("python.exe: No module named edge_tts");
        assert!(missing.contains("환경 설치(다시)"));
        assert!(!missing.contains("403"));
        let denied = python_failure("aiohttp.client_exceptions.WSServerHandshakeError: 403 Forbidden");
        assert!(denied.contains("403 Forbidden"));
        assert!(!denied.contains("패키지가 없어요"));
    }

    #[test]
    fn updated_protocol_is_used_before_the_legacy_handshake() {
        let (bytes, engine) = synthesize_from_clients(
            || Ok(vec![0xff, 0xf3, 1]),
            || panic!("Do not send the old handshake when the updated client succeeds"),
        ).unwrap();
        assert_eq!(engine, "edge-tts");
        assert!(!bytes.is_empty());
        let denied = synthesize_from_clients(
            || Err("403 Forbidden".into()),
            || Err("403 Forbidden".into()),
        ).unwrap_err();
        assert!(denied.contains("403 Forbidden"));
        assert!(!denied.contains("패키지가 없어요"));
    }

    #[test]
    fn drm_token_matches_the_edge_tts_package() {
        assert_eq!(
            drm_token(1_800_000_000.0),
            "FF4C72425863FDF9E7916FF23CB0CDF80CB5C3B2162FC8B03C37EFEB82BB6C89"
        );
        assert_eq!(
            drm_token(1_759_584_000.7),
            "26CE238A83894654AED6E0677218C0EADDFE1E33E1F083B0BB7D83793A301356"
        );
    }

    #[test]
    fn timestamps_look_like_javascript_dates() {
        assert_eq!(js_date_string(1_800_000_000), "Fri Jan 15 2027 08:00:00 GMT+0000 (Coordinated Universal Time)");
        assert_eq!(js_date_string(951_782_400), "Tue Feb 29 2000 00:00:00 GMT+0000 (Coordinated Universal Time)");
    }

    #[test]
    fn ssml_escapes_markup_in_the_sentence() {
        let markup = ssml("ko-KR-SunHiNeural", "a < b & c");
        assert!(markup.contains("a &lt; b &amp; c"));
        assert!(markup.contains("<voice name='ko-KR-SunHiNeural'>"));
        assert_eq!(connection_id().len(), 32);
        assert_ne!(connection_id(), connection_id());
    }

    #[test]
    fn rejects_unknown_voices_and_empty_text() {
        assert!(synthesize("system", "안녕").is_err());
        assert!(synthesize("ko-KR-SunHiNeural", "   ").is_err());
        assert!(is_known_voice("ko-KR-InJoonNeural"));
        assert!(!is_known_voice("system"));
    }

    #[test]
    fn cache_name_is_stable_and_distinct() {
        let a = cache_path("ko-KR-SunHiNeural", "안녕하세요").unwrap();
        let b = cache_path("ko-KR-SunHiNeural", "안녕하세요").unwrap();
        let c = cache_path("ko-KR-InJoonNeural", "안녕하세요").unwrap();
        let d = cache_path("ko-KR-SunHiNeural", "안녕하세요.").unwrap();
        assert_eq!(a, b);
        assert_ne!(a, c);
        assert_ne!(a, d);
        assert!(a.to_string_lossy().ends_with(".mp3"));
    }

    /// `cargo test --lib tts -- --ignored` talks to the real service.
    /// A never-cached phrase, so the connection path itself (timeouts included) is exercised.
    #[test]
    #[ignore]
    fn a_fresh_clip_downloads_within_the_timeouts() {
        let phrase = format!("지금 시각은 {}초예요", now_unix() as u64 % 100000);
        let started = std::time::Instant::now();
        let (bytes, engine) = synthesize(&default_voice(), &phrase).unwrap();
        assert!(!bytes.is_empty());
        assert_ne!(engine, "cache");
        assert!(started.elapsed() < std::time::Duration::from_secs(30), "{:?}", started.elapsed());
    }

    #[test]
    #[ignore]
    fn the_service_answers_with_mp3() {
        let (bytes, engine) = synthesize("ko-KR-SunHiNeural", "내장 음성 시험입니다.").unwrap();
        assert!(bytes.len() > 1000, "{engine}");
        assert!(bytes.starts_with(&[0xFF]) || bytes.starts_with(b"ID3"), "{engine}");
    }
}
