use crate::Unit;
use serde::{Deserialize, Serialize};
use std::{process::Stdio, time::Duration};
use tokio::{
    io::{AsyncRead, AsyncReadExt, AsyncWriteExt},
    process::Command,
};

const OUTPUT_LIMIT: u64 = 65536;

pub fn assemble(
    unit: &Unit,
    answers: &std::collections::HashMap<String, String>,
) -> Result<String, String> {
    if answers.len() != unit.blanks.len() {
        return Err("지정된 빈칸에만 답을 입력해 주세요.".into());
    }
    let mut code = unit.starter_code.clone();
    for blank in &unit.blanks {
        let answer = answers.get(blank).ok_or("빈칸 답이 없습니다.")?;
        if answer.contains("{{") || answer.len() > 65536 {
            return Err("빈칸 답을 확인해 주세요.".into());
        }
        code = code.replace(&format!("{{{{{blank}}}}}"), answer);
    }
    Ok(code)
}
#[derive(Clone, Serialize, Deserialize)]
pub struct Execution {
    pub stdout: String,
    pub stderr: String,
    pub success: bool,
    pub state: String,
}
#[derive(Clone, Serialize, Deserialize)]
pub struct TestCaseResult {
    pub input: String,
    pub expected: String,
    pub stdout: String,
    pub stderr: String,
    pub passed: bool,
    pub state: String,
}
#[derive(Clone, Serialize, Deserialize)]
pub struct TestReport {
    pub passed: bool,
    pub cases: Vec<TestCaseResult>,
}

async fn read_output<R: AsyncRead + Unpin>(pipe: R) -> std::io::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    pipe.take(OUTPUT_LIMIT + 1).read_to_end(&mut bytes).await?;
    Ok(bytes)
}

pub async fn run_python(code: &str, input: &str) -> Result<Execution, String> {
    execute_python(code, input, None).await
}

async fn execute_python(
    code: &str,
    input: &str,
    checker: Option<&str>,
) -> Result<Execution, String> {
    if code.len() > 65536 || input.len() > 65536 || checker.is_some_and(|c| c.len() > 65536) {
        return Err("코드와 입력은 각각 64KB 이하여야 합니다.".into());
    }
    let directory = tempfile::tempdir().map_err(|e| e.to_string())?;
    std::fs::write(directory.path().join("main.py"), code).map_err(|e| e.to_string())?;
    let executable = std::env::var("MOLIP_PYTHON").unwrap_or_else(|_| {
        if cfg!(windows) {
            "python".into()
        } else {
            "python3".into()
        }
    });
    let mut command = Command::new(executable);
    command
        .arg("-I")
        .arg("-u")
        .current_dir(directory.path())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    if let Some(checker) = checker {
        std::fs::write(directory.path().join("checker.py"), checker).map_err(|e| e.to_string())?;
        command
            .arg("checker.py")
            .arg(directory.path().join("main.py"));
    } else {
        command.arg("main.py");
    }
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let mut child = command.spawn().map_err(|e| {
        format!("Python을 실행할 수 없습니다. 설치와 실행 경로를 확인해 주세요: {e}")
    })?;
    let mut stdin = child.stdin.take().ok_or("입력 연결에 실패했습니다.")?;
    let stdout = child.stdout.take().ok_or("출력 연결에 실패했습니다.")?;
    let stderr = child
        .stderr
        .take()
        .ok_or("오류 출력 연결에 실패했습니다.")?;
    let input = input.as_bytes().to_vec();
    let collected = async {
        let write = async {
            let _ = stdin.write_all(&input).await;
            drop(stdin);
            Ok::<(), std::io::Error>(())
        };
        let (stdout, stderr, status, ()) = tokio::try_join!(
            read_output(stdout),
            read_output(stderr),
            child.wait(),
            write
        )?;
        Ok::<_, std::io::Error>((stdout, stderr, status))
    };
    match tokio::time::timeout(Duration::from_secs(5), collected).await {
        Ok(Ok((stdout, stderr, status))) => {
            let limited = stdout.len() as u64 > OUTPUT_LIMIT || stderr.len() as u64 > OUTPUT_LIMIT;
            Ok(Execution {
                stdout: String::from_utf8_lossy(&stdout[..stdout.len().min(OUTPUT_LIMIT as usize)])
                    .replace("\r\n", "\n"),
                stderr: String::from_utf8_lossy(&stderr[..stderr.len().min(OUTPUT_LIMIT as usize)])
                    .into(),
                success: status.success() && !limited,
                state: if limited {
                    "output_limit"
                } else if status.success() {
                    "finished"
                } else {
                    "runtime_error"
                }
                .into(),
            })
        }
        Ok(Err(error)) => {
            let _ = child.kill().await;
            Err(error.to_string())
        }
        Err(_) => {
            let _ = child.kill().await;
            Ok(Execution {
                stdout: String::new(),
                stderr: "실행 시간 제한 5초를 초과했습니다.".into(),
                success: false,
                state: "timeout".into(),
            })
        }
    }
}

fn normalized(value: &str) -> String {
    value
        .replace("\r\n", "\n")
        .trim_end_matches('\n')
        .to_string()
}

pub async fn check_unit(unit: &Unit, code: &str) -> Result<TestReport, String> {
    let mut cases = Vec::new();
    if let Some(checker) = unit.checker.as_deref().filter(|c| !c.trim().is_empty()) {
        let result = execute_python(code, "", Some(checker)).await?;
        cases.push(TestCaseResult {
            input: String::new(),
            expected: "검사 코드 종료 상태 0".into(),
            stdout: result.stdout,
            stderr: result.stderr,
            passed: result.success,
            state: result.state,
        });
    } else {
        if unit.tests.is_empty() || unit.tests.len() > 30 {
            return Err("입출력 테스트는 1개 이상 30개 이하로 등록해야 합니다.".into());
        }
        for test in &unit.tests {
            let result = run_python(code, &test.input).await?;
            let passed = result.success && normalized(&result.stdout) == normalized(&test.expected);
            cases.push(TestCaseResult {
                input: test.input.clone(),
                expected: test.expected.clone(),
                stdout: result.stdout,
                stderr: result.stderr,
                passed,
                state: result.state,
            });
        }
    }
    Ok(TestReport {
        passed: cases.iter().all(|c| c.passed),
        cases,
    })
}
