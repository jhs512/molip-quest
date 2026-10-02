use molip_quest::server::{router, AppState};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let database = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite://molip-server.sqlite3?mode=rwc".into());
    let state = AppState::connect(&database).await?;
    if let (Ok(email), Ok(password)) = (
        std::env::var("MOLIP_INSTRUCTOR_EMAIL"),
        std::env::var("MOLIP_INSTRUCTOR_PASSWORD"),
    ) {
        if let Err(error) = state.provision_instructor(&email, &password).await {
            use axum::response::IntoResponse;
            eprintln!(
                "Instructor setup returned {}",
                error.into_response().status()
            );
        }
    }
    let address = std::env::var("MOLIP_SERVER_BIND").unwrap_or_else(|_| "127.0.0.1:3010".into());
    let listener = tokio::net::TcpListener::bind(&address).await?;
    println!("Molip Quest server listening on {address}");
    axum::serve(listener, router(state)).await?;
    Ok(())
}
