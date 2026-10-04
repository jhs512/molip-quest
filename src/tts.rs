//! Neural Korean speech for 해설 모드 through the `edge-tts` Python package (Microsoft Edge's
//! online Read Aloud voices: 선히, 인준, 현수). The page asks for audio over the app's custom
//! protocol (`molip://localhost/tts`, `http://molip.localhost/tts` on Windows) and plays the MP3;
//! when the package is missing or the network is down the page falls back to the system voice.
//! Clips are cached under the app data folder, so a sentence is synthesized once.

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

/// MP3 bytes for the sentence, from the cache or freshly synthesized.
pub fn synthesize(voice: &str, text: &str) -> Result<Vec<u8>, String> {
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
            return Ok(bytes);
        }
    }
    let mut command = std::process::Command::new(crate::runner::python_executable());
    command
        .args(["-m", "edge_tts", "--voice", voice, "--text", text, "--write-media"])
        .arg(&path)
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::piped());
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000);
    }
    let output = command
        .output()
        .map_err(|e| format!("edge-tts를 실행하지 못했습니다: {e}"))?;
    if !output.status.success() {
        let _ = std::fs::remove_file(&path);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let reason = stderr.lines().rev().find(|l| !l.trim().is_empty()).unwrap_or("");
        return Err(format!("edge-tts 합성 실패: {reason}"));
    }
    let bytes = std::fs::read(&path).map_err(|e| e.to_string())?;
    if bytes.is_empty() {
        let _ = std::fs::remove_file(&path);
        return Err("edge-tts가 빈 파일을 만들었습니다.".into());
    }
    Ok(bytes)
}

#[cfg(test)]
mod tests {
    use super::*;

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
}
