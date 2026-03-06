#![no_std]
#![no_main]
#![feature(alloc_error_handler)]

mod lib;

extern crate alloc;
use uefi::prelude::*;
use alloc::vec;
use core::fmt::Write;
use lib::std::print;

// ---------------------- ENTRY POINT ----------------------
#[entry]
fn efi_main(handle: Handle, mut st: SystemTable<Boot>) -> Status {
    uefi_services::init(&mut st).unwrap();
    let _ = st.stdout().write_str("Bootloader: preparing kernel...\n");
    let mmap_size = st.boot_services().memory_map_size();
    let _mmap_storage = vec![0; mmap_size.map_size + 8 * mmap_size.entry_size];
    let _ = st.stdout().write_str("Bootloader: exiting boot services (no more UEFI console output)\n");
    let (_runtime_st, _memory_map) = st.exit_boot_services(); // eternal doom from this line onward
    kernel();
    // shut down (maybe)
    loop {
        unsafe { core::arch::asm!("hlt"); }
    }
}

// ---------------------- FREESTANDING KERNEL (FREEDOM AT LAST) ----------------------
fn kernel() {
    print("Hello world!");
}

// ---------------------- ALLOC ERROR HANDLER ----------------------
#[alloc_error_handler]
fn alloc_error(_: core::alloc::Layout) -> ! {
    loop { unsafe { core::arch::asm!("hlt"); } }
}