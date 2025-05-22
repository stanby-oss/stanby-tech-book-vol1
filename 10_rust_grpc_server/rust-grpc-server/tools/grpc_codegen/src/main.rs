use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    println!("Running code generation...");

    let proto_path ="../../proto";
    tonic_build::configure()
        .include_file("mod.rs")
        .file_descriptor_set_path("../../src/tonic_build_gen/descriptor.bin")
        .build_client(false)
        .build_server(true)
        .out_dir("../../src/tonic_build_gen")
        .compile_protos(
            &[
                format!("{}/user.proto", proto_path),
            ],
            &[proto_path],
        )?;
    println!("Code generation completed.");
    Ok(())

}
