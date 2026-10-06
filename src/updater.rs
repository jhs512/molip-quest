//! Auto-update from GitHub Releases (desktop only).
//!
//! Every push to main publishes a release tagged `v<version>-build.<run>` (release.yml) and the
//! workflow bakes that run number into the executable as `MOLIP_BUILD`. The app asks the API
//! for the latest release, compares build numbers, and when a newer one exists downloads this
//! platform's installer and hands over to a small script that waits for the app to exit,
//! installs, and starts the new build. Drafts and progress are saved as the student works, so
//! closing is safe at any moment.
//!
//! Development builds (no `MOLIP_BUILD`) never update themselves unless `MOLIP_UPDATE_CHECK=1`.
use std::path::PathBuf;

pub const REPO: &str = "jhs512/molip-quest";
const API_LATEST: &str = "https://api.github.com/repos/jhs512/molip-quest/releases/latest";

#[derive(Clone, Debug, PartialEq)]
pub struct Release {
    pub build: u64,
    pub tag: String,
    pub title: String,
    pub asset_name: String,
    pub asset_url: String,
    pub size: u64,
}

/// The build number this executable was published as; 0 for a development build.
pub fn current_build() -> u64 {
    option_env!("MOLIP_BUILD")
        .and_then(|b| b.trim().parse().ok())
        .unwrap_or(0)
}

/// Whether this build should look for updates at all.
pub fn enabled() -> bool {
    if cfg!(target_os = "android") {
        return false;
    }
    current_build() > 0 || std::env::var_os("MOLIP_UPDATE_CHECK").is_some()
}

/// "v0.1.0-build.42" → 42.
pub fn build_of(tag: &str) -> Option<u64> {
    tag.rsplit("build.").next()?.trim().parse().ok()
}

/// The installer this platform wants from a release's asset list.
pub fn asset_for_platform() -> Option<&'static str> {
    if cfg!(target_os = "windows") {
        Some("molip-quest-windows-x64-setup.exe")
    } else if cfg!(target_os = "macos") {
        Some("molip-quest-macos-arm64.dmg")
    } else {
        None
    }
}

/// The newer release in a `releases/latest` JSON body, or None when it is not newer than
/// `current` or carries no installer for this platform.
pub fn newer_in(json: &serde_json::Value, current: u64) -> Option<Release> {
    let tag = json["tag_name"].as_str()?;
    let build = build_of(tag)?;
    if build <= current {
        return None;
    }
    let wanted = asset_for_platform()?;
    let asset = json["assets"]
        .as_array()?
        .iter()
        .find(|a| a["name"].as_str() == Some(wanted))?;
    Some(Release {
        build,
        tag: tag.to_string(),
        title: json["name"].as_str().unwrap_or(tag).to_string(),
        asset_name: wanted.to_string(),
        asset_url: asset["browser_download_url"].as_str()?.to_string(),
        size: asset["size"].as_u64().unwrap_or(0),
    })
}

#[cfg(not(target_os = "android"))]
fn agent() -> ureq::Agent {
    use ureq::tls::{TlsConfig, TlsProvider};
    let config = ureq::Agent::config_builder()
        .tls_config(
            TlsConfig::builder()
                .provider(TlsProvider::NativeTls)
                .build(),
        )
        .user_agent(format!("molip-quest/{}", current_build()))
        .timeout_global(Some(std::time::Duration::from_secs(600)))
        .build();
    ureq::Agent::new_with_config(config)
}

/// Ask GitHub for the latest release. Blocking; call from a worker thread.
#[cfg(not(target_os = "android"))]
pub fn check() -> Result<Option<Release>, String> {
    if !enabled() {
        return Ok(None);
    }
    let mut response = agent()
        .get(API_LATEST)
        .header("Accept", "application/vnd.github+json")
        .call()
        .map_err(|e| format!("업데이트 확인 실패: {e}"))?;
    let json: serde_json::Value = response
        .body_mut()
        .read_json()
        .map_err(|e| format!("업데이트 정보를 읽지 못했습니다: {e}"))?;
    Ok(newer_in(&json, current_build()))
}

/// Download the release's installer into the app data folder, reporting (done, total) bytes.
/// Blocking; call from a worker thread.
#[cfg(not(target_os = "android"))]
pub fn download(release: &Release, mut progress: impl FnMut(u64, u64)) -> Result<PathBuf, String> {
    use std::io::{Read, Write};
    let dir = crate::data_dir()?.join("updates");
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join(format!("build-{}-{}", release.build, release.asset_name));
    let mut response = agent()
        .get(&release.asset_url)
        .call()
        .map_err(|e| format!("설치 파일을 받지 못했습니다: {e}"))?;
    let total = response
        .headers()
        .get("Content-Length")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.parse().ok())
        .unwrap_or(release.size);
    let mut reader = response.body_mut().with_config().limit(1 << 30).reader();
    let mut file = std::fs::File::create(&path).map_err(|e| e.to_string())?;
    let mut buffer = vec![0u8; 256 * 1024];
    let mut done = 0u64;
    loop {
        let n = reader
            .read(&mut buffer)
            .map_err(|e| format!("내려받는 중 끊겼습니다: {e}"))?;
        if n == 0 {
            break;
        }
        file.write_all(&buffer[..n]).map_err(|e| e.to_string())?;
        done += n as u64;
        progress(done, total);
    }
    file.flush().map_err(|e| e.to_string())?;
    if total > 0 && done != total {
        let _ = std::fs::remove_file(&path);
        return Err(format!(
            "설치 파일이 불완전합니다 ({done} / {total} 바이트)."
        ));
    }
    Ok(path)
}

#[cfg(target_os = "windows")]
fn windows_update_command(script: &str) -> std::process::Command {
    use std::os::windows::process::CommandExt;
    let mut command = std::process::Command::new("powershell");
    command.args([
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle",
        "Hidden",
        "-Command",
        script,
    ]);
    // Windows PowerShell exits without evaluating -Command when started with
    // DETACHED_PROCESS. CREATE_NO_WINDOW alone hides it and lets it outlive the app.
    command.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
    command.stdin(std::process::Stdio::null());
    command
}

/// Hand over to the installer and leave: a background script waits for this process to exit,
/// installs the new build over the current one and starts it. Returns only on failure.
#[cfg(not(target_os = "android"))]
pub fn install_and_restart(installer: &PathBuf) -> Result<(), String> {
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let pid = std::process::id();
    #[cfg(target_os = "windows")]
    {
        // Silent per-user reinstall into the same folder (Inno remembers it), then relaunch.
        let script = format!(
            "Wait-Process -Id {pid} -ErrorAction SilentlyContinue; \
             $p = Start-Process -FilePath '{installer}' -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CLOSEAPPLICATIONS' -Wait -PassThru; \
             Start-Process -FilePath '{exe}'",
            installer = installer.display().to_string().replace('\'', "''"),
            exe = exe.display().to_string().replace('\'', "''"),
        );
        windows_update_command(&script)
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn()
            .map_err(|e| format!("업데이트 스크립트를 시작하지 못했습니다: {e}"))?;
    }
    #[cfg(target_os = "macos")]
    {
        // The bundle is three levels above the binary: X.app/Contents/MacOS/molip-quest.
        let bundle = exe
            .ancestors()
            .nth(3)
            .filter(|p| p.extension().is_some_and(|e| e == "app"))
            .ok_or("앱 번들 밖에서 실행 중이라 자동 업데이트를 할 수 없습니다.")?
            .to_path_buf();
        let script = format!(
            "while kill -0 {pid} 2>/dev/null; do sleep 0.5; done; \
             mount=$(hdiutil attach '{dmg}' -nobrowse -readonly | awk -F'\\t' '/\\/Volumes\\//{{print $NF}}' | head -n 1); \
             app=$(ls -d \"$mount\"/*.app | head -n 1); \
             rm -rf '{bundle}'; ditto \"$app\" '{bundle}'; xattr -dr com.apple.quarantine '{bundle}' 2>/dev/null; \
             hdiutil detach \"$mount\" -quiet; open -n '{bundle}'",
            dmg = installer.display().to_string().replace('\'', "'\\''"),
            bundle = bundle.display().to_string().replace('\'', "'\\''"),
        );
        std::process::Command::new("sh")
            .args(["-c", &script])
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn()
            .map_err(|e| format!("업데이트 스크립트를 시작하지 못했습니다: {e}"))?;
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    {
        let _ = (exe, pid);
        return Err("이 플랫폼은 자동 업데이트를 지원하지 않습니다.".into());
    }
    #[allow(unreachable_code)]
    {
        std::process::exit(0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[cfg(target_os = "windows")]
    #[test]
    fn hidden_update_helper_actually_executes_its_script() {
        let output = windows_update_command("Write-Output 'updater-handoff-ready'")
            .output()
            .expect("launch update helper");
        assert!(output.status.success());
        assert_eq!(
            String::from_utf8_lossy(&output.stdout).trim(),
            "updater-handoff-ready",
            "PowerShell exited without running the update script"
        );
    }

    fn latest(tag: &str) -> serde_json::Value {
        serde_json::json!({
            "tag_name": tag,
            "name": format!("{tag} — subject"),
            "assets": [
                {"name": "molip-quest-windows-x64-setup.exe", "browser_download_url": "https://example.com/w.exe", "size": 10},
                {"name": "molip-quest-macos-arm64.dmg", "browser_download_url": "https://example.com/m.dmg", "size": 20},
                {"name": "molip-quest-android.apk", "browser_download_url": "https://example.com/a.apk", "size": 30}
            ]
        })
    }

    #[test]
    fn build_numbers_come_from_the_tag() {
        assert_eq!(build_of("v0.1.0-build.42"), Some(42));
        assert_eq!(build_of("v1.2.3-build.7"), Some(7));
        assert_eq!(build_of("v0.1.0"), None);
    }

    #[test]
    fn only_a_newer_release_with_this_platforms_installer_counts() {
        let newer = newer_in(&latest("v0.1.0-build.42"), 41);
        if let Some(wanted) = asset_for_platform() {
            let release = newer.expect("newer");
            assert_eq!(release.build, 42);
            assert_eq!(release.asset_name, wanted);
            assert!(release.asset_url.starts_with("https://example.com/"));
        } else {
            assert!(newer.is_none());
        }
        assert!(newer_in(&latest("v0.1.0-build.42"), 42).is_none());
        assert!(newer_in(&latest("v0.1.0-build.42"), 50).is_none());
        let mut no_assets = latest("v0.1.0-build.42");
        no_assets["assets"] = serde_json::json!([]);
        assert!(newer_in(&no_assets, 1).is_none());
    }

    /// Needs the network and ~40 MB: `cargo test -- --ignored installer_downloads`.
    #[test]
    #[ignore]
    #[cfg(not(target_os = "android"))]
    fn installer_downloads_completely() {
        std::env::set_var("MOLIP_UPDATE_CHECK", "1");
        let release = check().unwrap().expect("a release");
        let mut last = (0, 0);
        let path = download(&release, |done, total| last = (done, total)).unwrap();
        let size = std::fs::metadata(&path).unwrap().len();
        assert!(
            size > 1_000_000 && size == release.size,
            "{size} vs {}",
            release.size
        );
        let _ = std::fs::remove_file(path);
    }

    /// Needs the network: `cargo test -- --ignored latest_release`.
    #[test]
    #[ignore]
    #[cfg(not(target_os = "android"))]
    fn latest_release_is_reachable() {
        std::env::set_var("MOLIP_UPDATE_CHECK", "1");
        let found = check().unwrap();
        assert!(found.is_some(), "a release newer than build 0 should exist");
    }
}
