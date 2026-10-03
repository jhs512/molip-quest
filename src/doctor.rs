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
    let script = "import sys,json,importlib\nresult={'python':sys.version.split()[0]}\nfor name in ['pandas','matplotlib','seaborn','sklearn','openpyxl']:\n try:\n  module=importlib.import_module(name); result[name]=getattr(module,'__version__','설치됨')\n except Exception: result[name]=None\nprint(json.dumps(result))";
    let result = probe(&python, &["-I", "-X", "utf8", "-c", script])
        .await
        .and_then(|out| serde_json::from_slice::<serde_json::Value>(&out).ok());
    checks.push(Check {
        name: "Python 실행".into(),
        ready: result.is_some(),
        detail: result
            .as_ref()
            .and_then(|v| v["python"].as_str())
            .map(|v| format!("버전 {v}"))
            .unwrap_or_else(|| "Python을 설치하거나 실행 경로를 설정하세요.".into()),
    });
    for (key, name) in [
        ("pandas", "pandas · 표 분석"),
        ("matplotlib", "matplotlib · 그래프"),
        ("seaborn", "seaborn · 시각화"),
        ("sklearn", "scikit-learn · 모델 학습"),
        ("openpyxl", "openpyxl · Excel 읽기"),
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
    checks.extend(inspect_ai().await);
    checks
}

pub async fn inspect_ai() -> Vec<Check> {
    let mut checks = Vec::new();
    let claude = std::env::var("MOLIP_CLAUDE_PATH").unwrap_or_else(|_| "claude".into());
    let installed = probe(&claude, &["--version"]).await.is_some();
    checks.push(Check {
        name: "Claude Code CLI".into(),
        ready: installed,
        detail: if installed {
            "실행할 수 있습니다."
        } else {
            "Claude Code를 설치하거나 실행 경로를 설정하세요."
        }
        .into(),
    });
    let auth = if installed {
        probe(&claude, &["auth", "status", "--json"])
            .await
            .and_then(|out| serde_json::from_slice::<serde_json::Value>(&out).ok())
    } else {
        None
    };
    let logged_in = auth
        .as_ref()
        .is_some_and(|v| v["loggedIn"].as_bool() == Some(true));
    checks.push(Check {
        name: "Claude 로그인".into(),
        ready: logged_in,
        detail: if logged_in {
            "로그인되어 있습니다. 실제 요청은 사용 한도에 따라 달라질 수 있습니다."
        } else {
            "Claude Code에서 로그인한 뒤 다시 검사하세요."
        }
        .into(),
    });
    checks
}
