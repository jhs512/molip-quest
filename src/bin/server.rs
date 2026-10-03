use molip_quest::server::{router, AppState};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    let database = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite://molip-server.sqlite3?mode=rwc".into());
    let state = AppState::connect(&database).await?;
    for role in ["INSTRUCTOR", "ADMIN"] {
        if let (Ok(email), Ok(password)) = (
            std::env::var(format!("MOLIP_{role}_EMAIL")),
            std::env::var(format!("MOLIP_{role}_PASSWORD")),
        ) {
            let result = if role == "ADMIN" {
                state.provision_admin(&email, &password).await
            } else {
                state.provision_instructor(&email, &password).await
            };
            if let Err(error) = result {
                use axum::response::IntoResponse;
                eprintln!("{role} setup returned {}", error.into_response().status());
            }
        }
    }
    let address = std::env::var("MOLIP_SERVER_BIND").unwrap_or_else(|_| "127.0.0.1:3010".into());
    let listener = tokio::net::TcpListener::bind(&address).await?;
    println!("Molip Quest server listening on {address}");
    axum::serve(listener, router(state)).await?;
    Ok(())
}
