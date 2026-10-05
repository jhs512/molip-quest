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
            .unwrap_or_else(|| format!("Python을 설치하거나 실행 경로를 설정하세요. (시도한 경로: {python})")),
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
