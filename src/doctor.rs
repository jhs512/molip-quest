use crate::runner::python_executable;
use serde::{Deserialize, Serialize};
use std::process::Stdio;
use tokio::process::Command;

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub struct Check {
    pub name: String,
    pub ready: bool,
    pub detail: String,
}

async fn probe(executable: &str, args: &[&str]) -> Option<Vec<u8>> {
    let mut command = Command::new(executable);
    command
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .kill_on_drop(true);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let child = command.spawn().ok()?;
    let output = tokio::time::timeout(std::time::Duration::from_secs(20), child.wait_with_output())
        .await
        .ok()?
        .ok()?;
    (output.status.success() && output.stdout.len() <= 65536).then_some(output.stdout)
}

pub async fn inspect() -> Vec<Check> {
    let mut checks = Vec::new();
    let python = python_executable();
    let script = "import sys,json,importlib\nresult={'python':sys.version.split()[0]}\nfor name in ['pandas','matplotlib','seaborn','sklearn','openpyxl','bs4','requests','FinanceDataReader','yfinance']:\n try:\n  module=importlib.import_module(name); result[name]=getattr(module,'__version__','설치됨')\n except Exception: result[name]=None\nprint(json.dumps(result))";
    let result = probe(&python, &["-I", "-X", "utf8", "-c", script])
        .await
        .and_then(|out| serde_json::from_slice::<serde_json::Value>(&out).ok());
    checks.push(Check {
        name: "Python 실행".into(),
        ready: result.is_some(),
        detail: result
            .as_ref()
            .and_then(|v| v["python"].as_str())
            .map(|v| format!("버전 {v} · {python}"))
            .unwrap_or_else(|| {
                format!("Python을 설치하거나 실행 경로를 설정하세요. (시도한 경로: {python})")
            }),
    });
    for (key, name) in [
        ("pandas", "pandas · 표 분석"),
        ("matplotlib", "matplotlib · 그래프"),
        ("seaborn", "seaborn · 시각화"),
        ("sklearn", "scikit-learn · 모델 학습"),
        ("openpyxl", "openpyxl · Excel 읽기"),
        ("bs4", "BeautifulSoup · HTML 분석"),
        ("requests", "requests · 웹 페이지 받기"),
        ("FinanceDataReader", "FinanceDataReader · 주가 받기"),
        ("yfinance", "yfinance · 주가 받기 (야후)"),
    ] {
        let version = result.as_ref().and_then(|v| v[key].as_str());
        checks.push(Check {
            name: name.into(),
            ready: version.is_some(),
            detail: version
                .map(|v| format!("버전 {v}"))
                .unwrap_or_else(|| "선택한 Python 환경에 패키지를 설치하세요.".into()),
        });
    }
    checks
}

// ---- 환경 설치: a fresh learning Python in the app data folder, for this OS. ----

/// The learning packages, pinned (the same file the setup scripts read).
const REQUIREMENTS: &str = include_str!("../requirements-learning.txt");

/// Where `uv` usually lands after its installer, besides PATH.
fn uv_candidates() -> Vec<std::path::PathBuf> {
    let mut out = vec![std::path::PathBuf::from("uv")];
    if let Some(home) = std::env::var_os("USERPROFILE").or_else(|| std::env::var_os("HOME")) {
        let home = std::path::PathBuf::from(home);
        out.push(
            home.join(".local")
                .join("bin")
                .join(if cfg!(windows) { "uv.exe" } else { "uv" }),
        );
        out.push(
            home.join(".cargo")
                .join("bin")
                .join(if cfg!(windows) { "uv.exe" } else { "uv" }),
        );
    }
    if !cfg!(windows) {
        out.push("/opt/homebrew/bin/uv".into());
        out.push("/usr/local/bin/uv".into());
    }
    out
}

async fn find_uv() -> Option<String> {
    for candidate in uv_candidates() {
        let path = candidate.to_string_lossy().into_owned();
        if probe(&path, &["--version"]).await.is_some() {
            return Some(path);
        }
    }
    None
}

/// Select a real patch-version directory without following uv's minor-version
/// junction. Merely querying python.exe through that junction can fail with 448.
#[cfg(windows)]
fn direct_windows_python(store: &std::path::Path) -> Option<std::path::PathBuf> {
    use std::os::windows::fs::MetadataExt;
    std::fs::read_dir(store)
        .ok()?
        .filter_map(Result::ok)
        .filter_map(|entry| {
            let name = entry.file_name();
            let patch = name
                .to_str()?
                .strip_prefix("cpython-3.13.")?
                .strip_suffix("-windows-x86_64-none")?
                .parse::<u32>()
                .ok()?;
            let metadata = std::fs::symlink_metadata(entry.path()).ok()?;
            if !metadata.is_dir() || metadata.file_attributes() & 0x400 != 0 {
                return None;
            }
            let python = entry.path().join("python.exe");
            python.is_file().then_some((patch, python))
        })
        .max_by_key(|(patch, _)| *patch)
        .map(|(_, path)| path)
}

#[cfg(windows)]
fn copy_python_runtime(source: &std::path::Path, target: &std::path::Path) -> Result<(), String> {
    use std::os::windows::fs::MetadataExt;
    let metadata = std::fs::symlink_metadata(source).map_err(|e| e.to_string())?;
    if metadata.file_attributes() & 0x400 != 0 {
        return Err(format!(
            "Python 원본에 연결 파일이 있습니다: {}",
            source.display()
        ));
    }
    if metadata.is_dir() {
        std::fs::create_dir_all(target).map_err(|e| e.to_string())?;
        for entry in std::fs::read_dir(source).map_err(|e| e.to_string())? {
            let entry = entry.map_err(|e| e.to_string())?;
            // This new copy belongs to the app, not to uv's managed installation.
            if entry.file_name() == "EXTERNALLY-MANAGED" {
                continue;
            }
            copy_python_runtime(&entry.path(), &target.join(entry.file_name()))?;
        }
    } else {
        std::fs::copy(source, target).map_err(|e| e.to_string())?;
    }
    Ok(())
}

async fn create_learning_environment(
    report: &tokio::sync::mpsc::UnboundedSender<String>,
    uv: &str,
    env_dir: &std::path::Path,
    store: &std::path::Path,
) -> Result<(), String> {
    #[cfg(windows)]
    {
        if direct_windows_python(store).is_none() {
            let result = run_logged(
                report,
                uv,
                &[
                    "python",
                    "install",
                    "3.13",
                    "--no-bin",
                    "--no-registry",
                    "--no-config",
                ],
                Some(store),
            )
            .await;
            // uv can finish extracting Python and then fail to create the minor
            // junction. The extracted interpreter is still usable directly.
            if let Err(error) = result {
                if direct_windows_python(store).is_none() {
                    return Err(error);
                }
                let _ = report
                    .send("연결 경로 생성은 실패했지만 실제 Python 파일로 계속합니다.".into());
            }
        }
        let python =
            direct_windows_python(store).ok_or("실제 Python 3.13 설치 폴더를 찾지 못했습니다.")?;
        let python_str = python.to_string_lossy().into_owned();
        let _ = report.send(format!("연결 경로 없이 실행: {python_str}"));
        let _ = report.send("Python 본체와 라이브러리를 독립된 학습 환경으로 복사합니다 (가상환경 중계 파일 없이 실행).".into());
        return copy_python_runtime(python.parent().ok_or("Python 폴더가 없습니다.")?, env_dir);
    }
    #[cfg(not(windows))]
    let env_str = env_dir.to_string_lossy().into_owned();
    #[cfg(not(windows))]
    run_logged(
        report,
        uv,
        &["venv", &env_str, "--python", "3.13", "--managed-python"],
        Some(store),
    )
    .await
}

/// Run a command, streaming every output line to `report`; Err on a non-zero exit.
async fn run_logged(
    report: &tokio::sync::mpsc::UnboundedSender<String>,
    program: &str,
    args: &[&str],
    python_store: Option<&std::path::Path>,
) -> Result<(), String> {
    use tokio::io::{AsyncBufReadExt, BufReader};
    let mut command = Command::new(program);
    if let Some(store) = python_store {
        // Keep uv away from the shared Roaming installation: Windows cloud/reparse
        // filters can reject its interpreter junction with OS error 448.
        command.env("UV_PYTHON_INSTALL_DIR", store);
    }
    command
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let mut child = command
        .spawn()
        .map_err(|e| format!("{program} 실행 실패: {e}"))?;
    let stdout = child.stdout.take().map(|o| BufReader::new(o).lines());
    let stderr = child.stderr.take().map(|o| BufReader::new(o).lines());
    let out_report = report.clone();
    let err_report = report.clone();
    let out_task = tokio::spawn(async move {
        if let Some(mut lines) = stdout {
            while let Ok(Some(line)) = lines.next_line().await {
                let _ = out_report.send(line);
            }
        }
    });
    let err_task = tokio::spawn(async move {
        if let Some(mut lines) = stderr {
            while let Ok(Some(line)) = lines.next_line().await {
                let _ = err_report.send(line);
            }
        }
    });
    let status = tokio::time::timeout(std::time::Duration::from_secs(1800), child.wait())
        .await
        .map_err(|_| "30분 안에 끝나지 않았습니다.".to_string())?
        .map_err(|e| e.to_string())?;
    let _ = out_task.await;
    let _ = err_task.await;
    if status.success() {
        Ok(())
    } else {
        Err(format!(
            "{program} {} 실패 ({status})",
            args.first().copied().unwrap_or("")
        ))
    }
}

/// Install (or reinstall) the learning Python environment in the app data folder: get `uv`
/// if it is missing, create a fresh Python 3.13 venv, install the pinned packages. Progress
/// lines go to `report`; the result names the interpreter.
pub async fn install(report: tokio::sync::mpsc::UnboundedSender<String>) -> Result<String, String> {
    let data_dir = crate::data_dir()?;
    let env_dir = data_dir.join("ml-env");
    let python_store = data_dir.join("python");
    let say = |line: &str| {
        let _ = report.send(line.to_string());
    };
    say("[1/3] uv (Python 패키지 설치 도구)를 확인합니다.");
    let uv = match find_uv().await {
        Some(uv) => uv,
        None => {
            say("uv가 없어 받습니다 (astral.sh).");
            if cfg!(windows) {
                run_logged(
                    &report,
                    "powershell",
                    &[
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "ByPass",
                        "-Command",
                        "irm https://astral.sh/uv/install.ps1 | iex",
                    ],
                    None,
                )
                .await?;
            } else {
                run_logged(
                    &report,
                    "sh",
                    &["-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
                    None,
                )
                .await?;
            }
            find_uv()
                .await
                .ok_or("uv를 설치했지만 찾지 못했습니다. 앱을 다시 열고 시도하세요.")?
        }
    };
    say(&format!("uv: {uv}"));
    say(&format!(
        "앱 전용 Python 저장 위치: {}",
        python_store.display()
    ));
    say(&format!(
        "[2/3] Python 3.13 환경을 새로 만듭니다: {}",
        env_dir.display()
    ));
    if env_dir.exists() {
        std::fs::remove_dir_all(&env_dir)
            .map_err(|e| format!("예전 환경을 지우지 못했습니다: {e}"))?;
    }
    create_learning_environment(&report, &uv, &env_dir, &python_store).await?;
    let python = env_dir.join(if cfg!(windows) {
        "python.exe"
    } else {
        "bin/python"
    });
    say("[3/3] 수업 패키지를 설치합니다 (pandas, scikit-learn, matplotlib, seaborn, openpyxl, BeautifulSoup, requests, FinanceDataReader, yfinance). 몇 분 걸립니다.");
    let requirements =
        std::env::temp_dir().join(format!("molip-requirements-{}.txt", std::process::id()));
    std::fs::write(&requirements, REQUIREMENTS).map_err(|e| e.to_string())?;
    let python_str = python.to_string_lossy().into_owned();
    let req_str = requirements.to_string_lossy().into_owned();
    let mut package_args = vec!["pip", "install", "--python", &python_str, "-r", &req_str];
    if cfg!(windows) {
        package_args.extend([
            "--system",
            "--link-mode",
            "copy",
            "--no-config",
            "--no-managed-python",
            "--no-python-downloads",
        ]);
    }
    let result = run_logged(&report, &uv, &package_args, Some(&python_store)).await;
    let _ = std::fs::remove_file(&requirements);
    result?;
    Ok(format!("설치 완료 · {python_str}"))
}

#[cfg(test)]
mod install_tests {
    /// Confirm the old path used the minor junction, then make that alias unusable
    /// and verify the new environment uses and runs the real patch interpreter.
    #[cfg(windows)]
    #[tokio::test]
    #[ignore = "requires uv and Python download"]
    async fn environment_bypasses_unusable_minor_alias() {
        let uv = super::find_uv().await.expect("uv must be installed");
        let root = std::env::temp_dir().join(format!(
            "molip-python-alias-test-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let store = root.join("python");
        let (tx, _rx) = tokio::sync::mpsc::unbounded_channel();
        super::run_logged(
            &tx,
            &uv,
            &[
                "python",
                "install",
                "3.13",
                "--no-bin",
                "--no-registry",
                "--no-config",
            ],
            Some(&store),
        )
        .await
        .unwrap();
        let old_env = root.join("old-env");
        let old_str = old_env.to_string_lossy();
        super::run_logged(
            &tx,
            &uv,
            &[
                "venv",
                &old_str,
                "--python",
                "3.13",
                "--managed-python",
                "--no-python-downloads",
                "--no-config",
            ],
            Some(&store),
        )
        .await
        .unwrap();
        let old_config = std::fs::read_to_string(old_env.join("pyvenv.cfg")).unwrap();
        assert!(old_config.contains("cpython-3.13-windows-x86_64-none"));
        let minor = store.join("cpython-3.13-windows-x86_64-none");
        // remove_dir removes only this test-created junction, never its contents.
        std::fs::remove_dir(&minor).unwrap();
        std::fs::create_dir(&minor).unwrap();
        std::fs::write(minor.join("python.exe"), "unusable minor alias").unwrap();
        let env = root.join("new-env");
        super::create_learning_environment(&tx, &uv, &env, &store)
            .await
            .unwrap();
        // The copied runtime must not depend on the original store or a venv launcher.
        let canonical_root = std::fs::canonicalize(&root).unwrap();
        assert!(std::fs::canonicalize(&store)
            .unwrap()
            .starts_with(&canonical_root));
        std::fs::rename(&store, root.join("source-unavailable")).unwrap();
        let python = env.join("python.exe");
        let output = super::probe(
            &python.to_string_lossy(),
            &["-c", "import sys,ssl,sqlite3; print(sys.version_info[:2])"],
        )
        .await
        .unwrap();
        assert_eq!(String::from_utf8_lossy(&output).trim(), "(3, 13)");
        assert!(!env.join("pyvenv.cfg").exists());
        assert!(!env.join("Scripts/python.exe").exists());
        assert!(!env.join("Lib/EXTERNALLY-MANAGED").exists());
        // root is a unique temporary fixture containing no remaining junctions.
        assert!(std::fs::canonicalize(&root)
            .unwrap()
            .starts_with(std::fs::canonicalize(std::env::temp_dir()).unwrap()));
        std::fs::remove_dir_all(&root).unwrap();
    }

    /// Exercises the real uv subprocess without downloading Python or packages.
    #[tokio::test]
    #[ignore = "requires uv"]
    async fn uv_uses_app_python_store() {
        let uv = super::find_uv().await.expect("uv must be installed");
        let store = crate::data_dir().unwrap().join("python");
        let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel();
        super::run_logged(&tx, &uv, &["python", "dir"], Some(&store))
            .await
            .unwrap();
        drop(tx);
        let actual = rx.recv().await.expect("uv must report its Python store");
        assert_eq!(std::path::PathBuf::from(actual.trim()), store);
    }

    /// Needs the network and a few minutes: `cargo test -- --ignored environment_installs`.
    /// Creates the managed environment in the real app data folder.
    #[tokio::test]
    #[ignore]
    async fn environment_installs_and_passes_the_checks() {
        let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel::<String>();
        let worker = tokio::spawn(super::install(tx));
        while let Some(line) = rx.recv().await {
            eprintln!("{line}");
        }
        let done = worker.await.unwrap().unwrap();
        eprintln!("{done}");
        assert!(done.contains("ml-env"));
        let python = done.trim_start_matches("설치 완료 · ").to_string();
        // A cold package import can take longer than the interactive diagnostic
        // probe's 20 seconds (antivirus scanning and first-use caches on Windows).
        let mut command = tokio::process::Command::new(&python);
        command.args([
                "-I",
                "-c",
                "import pandas, sklearn, matplotlib, seaborn, openpyxl, bs4, requests, FinanceDataReader, yfinance; print('ok')",
            ]).kill_on_drop(true);
        #[cfg(windows)]
        command.creation_flags(0x08000000);
        let output = tokio::time::timeout(std::time::Duration::from_secs(120), command.output())
            .await
            .expect("freshly installed packages must import within two minutes")
            .unwrap();
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ok");
    }
}
