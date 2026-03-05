#![no_std]
#![no_main]
#![feature(alloc_error_handler)]

extern crate alloc;
use uefi::prelude::*;
use alloc::vec;
use core::fmt::Write;

// ---------------------- ENTRY POINT ----------------------
#[entry]
fn efi_main(handle: Handle, mut st: SystemTable<Boot>) -> Status {
    // Initialize UEFI services if needed
    uefi_services::init(&mut st).unwrap();

    // Optional: print a message using UEFI
    let _ = st.stdout().write_str("UEFI loader: preparing kernel...\n");

    // Get memory map and exit boot services
    let mmap_size = st.boot_services().memory_map_size();
    let _mmap_storage = vec![0; mmap_size.map_size + 8 * mmap_size.entry_size];
    let (_runtime_st, _memory_map) = st.exit_boot_services();

    // Now UEFI is gone, we are in "kernel mode"
    kernel();

    // Halt forever
    loop {
        unsafe { core::arch::asm!("hlt"); }
    }
}

// ---------------------- FREESTANDING KERNEL ----------------------
fn kernel() {
    // Direct hardware access: VGA text buffer example
    let vga_buffer = 0xb8000 as *mut u8;
    let msg = b"Hello, freestanding kernel!";
    for (i, &byte) in msg.iter().enumerate() {
        unsafe {
            *vga_buffer.add(i * 2) = byte;
            *vga_buffer.add(i * 2 + 1) = 0x0f; // White on black
        }
    }

    // Example: busy loop
    for _ in 0..1_000_000 {
        unsafe { core::arch::asm!("nop"); }
    }
}

// ---------------------- ALLOC ERROR HANDLER ----------------------
#[alloc_error_handler]
fn alloc_error(_: core::alloc::Layout) -> ! {
    loop { unsafe { core::arch::asm!("hlt"); } }
}