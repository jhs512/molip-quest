// Embed the quest icon into the Windows executable so Explorer, the taskbar and the
// Start menu show it. Other platforms get their icon from the packaging scripts.
fn main() {
    println!("cargo:rerun-if-changed=assets/icon/icon.ico");
    #[cfg(windows)]
    {
        let mut resource = winresource::WindowsResource::new();
        resource.set_icon("assets/icon/icon.ico");
        resource.compile().expect("embed Windows icon");
    }
}
