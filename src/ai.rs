use crate::{runner::assemble, Unit};
use serde_json::{json, Value};
use std::{collections::HashMap, time::Duration};

#[derive(Clone, PartialEq)]
pub struct AiConnection {
    pub base: String,
    pub model: String,
    pub key: String,
}
pub struct AiAnswer {
    pub message: String,
    pub code: Option<String>,
    pub answers: HashMap<String, String>,
}
impl Default for AiConnection {
    fn default() -> Self {
        Self {
            base: std::env::var("MOLIP_AI_BASE_URL").unwrap_or_else(|_| "claude-cli".into()),
            model: std::env::var("MOLIP_AI_MODEL").unwrap_or_else(|_| "auto".into()),
            key: std::env::var("MOLIP_AI_KEY").unwrap_or_default(),
        }
    }
}
impl AiConnection {
    pub async fn ask(
        &self,
        unit: &Unit,
        code: &str,
        question: &str,
        edit: bool,
    ) -> Result<AiAnswer, String> {
        if self.model.trim().is_empty() || question.trim().is_empty() {
            return Err("모델과 질문을 입력해 주세요.".into());
        }
        let format = if edit && unit.blanks.is_empty() {
            "JSON 객체로 message(설명)와 code(전체 수정 Python 코드)를 반환하세요."
        } else if edit {
            "JSON 객체로 message(설명)와 answers(빈칸 ID별 답 문자열 객체)를 반환하세요. 고정 코드를 변경하지 마세요."
        } else {
            "학생이 이해할 수 있는 설명과 힌트를 일반 텍스트로 제공하세요."
        };
        let content=json!({"lesson":unit.title,"instructions":unit.content,"student_code":code,"blank_ids":unit.blanks,"question":question}).to_string();
        let response_text = if self.base.trim() == "claude-cli" {
            self.claude_reply(
                &content,
                &format!("당신은 Python 학습 도우미입니다. {format}"),
            )
            .await?
        } else {
            self.http_reply(
                &content,
                &format!("당신은 Python 학습 도우미입니다. {format}"),
            )
            .await?
        };
        let text = response_text.as_str();
        if !edit {
            return Ok(AiAnswer {
                message: text.into(),
                code: None,
                answers: HashMap::new(),
            });
        }
        self.parse_edit(unit, text)
    }

    async fn http_reply(&self, content: &str, system: &str) -> Result<String, String> {
        let url =
            reqwest::Url::parse(self.base.trim()).map_err(|_| "AI 연결 주소를 확인해 주세요.")?;
        if url.scheme() != "http" && url.scheme() != "https" {
            return Err("AI 연결에는 HTTP 또는 HTTPS 주소가 필요합니다.".into());
        }
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(60))
            .build()
            .map_err(|_| "AI 연결을 준비할 수 없습니다.")?;
        let mut request=client.post(format!("{}/chat/completions",self.base.trim().trim_end_matches('/')))
            .json(&json!({"model":self.model,"messages":[{"role":"system","content":system},{"role":"user","content":content}]}));
        if !self.key.is_empty() {
            request = request.bearer_auth(&self.key);
        }
        let response = request
            .send()
            .await
            .map_err(|_| "AI에 연결할 수 없습니다. 도구 실행과 연결 설정을 확인해 주세요.")?;
        if !response.status().is_success() {
            return Err(format!(
                "AI 요청이 거부되었습니다 ({}). 연결 권한과 사용 한도를 확인해 주세요.",
                response.status().as_u16()
            ));
        }
        let body: Value = response
            .json()
            .await
            .map_err(|_| "AI 응답을 읽을 수 없습니다.")?;
        let text = body["choices"][0]["message"]["content"]
            .as_str()
            .ok_or("AI가 텍스트 응답을 반환하지 않았습니다.")?;
        Ok(text.to_string())
    }

    async fn claude_reply(&self, content: &str, system: &str) -> Result<String, String> {
        use std::process::Stdio;
        use tokio::{
            io::{AsyncReadExt, AsyncWriteExt},
            process::Command,
        };
        let directory = tempfile::tempdir().map_err(|_| "AI 실행 폴더를 준비할 수 없습니다.")?;
        let executable = std::env::var("MOLIP_CLAUDE_PATH").unwrap_or_else(|_| "claude".into());
        let mut command = Command::new(executable);
        command
            .args([
                "--print",
                "--output-format",
                "json",
                "--tools",
                "",
                "--no-session-persistence",
                "--max-turns",
                "1",
                "--system-prompt",
                system,
            ])
            .current_dir(directory.path())
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .kill_on_drop(true);
        if self.model != "auto" && !self.model.is_empty() {
            command.args(["--model", &self.model]);
        }
        #[cfg(windows)]
        command.creation_flags(0x08000000);
        let mut child = command
            .spawn()
            .map_err(|_| "Claude Code를 실행할 수 없습니다. 설치와 실행 경로를 확인해 주세요.")?;
        let mut stdin = child
            .stdin
            .take()
            .ok_or("Claude 입력 연결에 실패했습니다.")?;
        let stdout = child
            .stdout
            .take()
            .ok_or("Claude 출력 연결에 실패했습니다.")?;
        let stderr = child
            .stderr
            .take()
            .ok_or("Claude 오류 연결에 실패했습니다.")?;
        let future = async {
            let read_out = async {
                let mut output = Vec::new();
                stdout.take(1048577).read_to_end(&mut output).await?;
                Ok::<_, std::io::Error>(output)
            };
            let read_err = async {
                let mut output = Vec::new();
                stderr.take(1048577).read_to_end(&mut output).await?;
                Ok::<_, std::io::Error>(output)
            };
            let write = async {
                stdin.write_all(content.as_bytes()).await?;
                drop(stdin);
                Ok::<_, std::io::Error>(())
            };
            let (stdout, stderr, status, ()) =
                tokio::try_join!(read_out, read_err, child.wait(), write)?;
            Ok::<_, std::io::Error>((stdout, stderr, status))
        };
        let (stdout, stderr, status) =
            match tokio::time::timeout(Duration::from_secs(90), future).await {
                Ok(Ok(result)) => result,
                Ok(Err(_)) => {
                    let _ = child.kill().await;
                    return Err("Claude Code 입출력 연결에 실패했습니다.".into());
                }
                Err(_) => {
                    let _ = child.kill().await;
                    return Err("Claude Code 응답 시간이 초과되었습니다.".into());
                }
            };
        if stdout.len() > 1048576 || stderr.len() > 1048576 {
            return Err("Claude Code 응답이 너무 큽니다.".into());
        }
        if !status.success() {
            return Err(
                "Claude Code 요청이 실패했습니다. CLI 로그인과 사용 권한을 확인해 주세요.".into(),
            );
        }
        let value: Value = serde_json::from_slice(&stdout)
            .map_err(|_| "Claude Code 응답 형식을 읽을 수 없습니다.")?;
        if value["is_error"].as_bool() == Some(true) {
            return Err(
                "Claude Code가 요청을 완료하지 못했습니다. 로그인과 사용 한도를 확인해 주세요."
                    .into(),
            );
        }
        value["result"]
            .as_str()
            .map(str::to_string)
            .ok_or_else(|| "Claude Code 응답에 결과가 없습니다.".into())
    }

    fn parse_edit(&self, unit: &Unit, text: &str) -> Result<AiAnswer, String> {
        let text = text
            .trim()
            .strip_prefix("```json")
            .or_else(|| text.trim().strip_prefix("```"))
            .unwrap_or(text)
            .trim()
            .trim_end_matches("```")
            .trim();
        let parsed: Value = serde_json::from_str(text)
            .map_err(|_| "AI의 코드 변경 형식이 올바르지 않습니다. 다시 요청해 주세요.")?;
        let message = parsed["message"]
            .as_str()
            .unwrap_or("코드를 수정했습니다.")
            .to_string();
        let (code, answers) = if unit.blanks.is_empty() {
            (
                parsed["code"]
                    .as_str()
                    .ok_or("AI 응답에 수정 코드가 없습니다.")?
                    .to_string(),
                HashMap::new(),
            )
        } else {
            let answers: HashMap<String, String> =
                serde_json::from_value(parsed["answers"].clone())
                    .map_err(|_| "AI의 빈칸 답 형식이 올바르지 않습니다.")?;
            (assemble(unit, &answers)?, answers)
        };
        if code.len() > 65536 {
            return Err("AI가 반환한 코드가 너무 큽니다.".into());
        }
        Ok(AiAnswer {
            message,
            code: Some(code),
            answers,
        })
    }
}
