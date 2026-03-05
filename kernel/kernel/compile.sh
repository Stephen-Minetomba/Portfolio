#!/bin/bash
rustup install nightly
rustup default nightly
rustup component add rust-src llvm-tools-preview
cargo build --release --target x86_64-unknown-uefi
mv target/x86_64-unknown-uefi/release/kernel.efi ./kernel.efi
rm -rf Cargo.lock target
cd ../run
./copy.sh
cd ../kernel
