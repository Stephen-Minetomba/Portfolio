//! ====================================================================================================
//! Usage in main file:
//! ```rust
//! use lib::clock::{Rtc, DateTime};
//! fn kernel() {
//!     let now: DateTime = Rtc::now();
//!     // Access via: now.second, now.minute, now.hour, now.day, now.month, now.year
//! }
//! ```
//! Permanent issues:
//! - Even though this will patch immediately as soon as 2100 is reached, it is worth noting that it will display the year 2000 instead of 2100 in a century because it assumes year is 20xx due to the fact that the RTC returns only the last two digits (where x is a placeholder for a digit).
//! Fixed issues:
//! - Handles leap years (no fix needed in the first place, but just an important thing to note for other programmers).
//! Fixable medium issues:
//! - Does not handle leap seconds (about 1-2 per year). Handle them in userland, not the kernel, this is because you need to be in sync with NTP.
//! - Does not handle miliseconds.
//! Fixable small issues:
//! - Does not handle microseconds (big issue for HFT firms).
//! - Does not handle nanoseconds (big issue for HFT firms).
//! - Does not handle UTC offsets (must handle in userland).
//! ====================================================================================================
#![no_std]

use core::arch::asm;

pub struct Rtc;

#[derive(Debug, Clone, Copy)]
pub struct DateTime {
    pub second: u8,
    pub minute: u8,
    pub hour: u8,
    pub day: u8,
    pub month: u8,
    pub year: u16,
}

impl Rtc {
    pub fn now() -> DateTime {
        while Rtc::read_register(0x0A) & 0x80 != 0 {}
        let second = Rtc::bcd_to_bin(Rtc::read_register(0x00));
        let minute = Rtc::bcd_to_bin(Rtc::read_register(0x02));
        let hour = Rtc::bcd_to_bin(Rtc::read_register(0x04));
        let day = Rtc::bcd_to_bin(Rtc::read_register(0x07));
        let month = Rtc::bcd_to_bin(Rtc::read_register(0x08));
        let year = Rtc::bcd_to_bin(Rtc::read_register(0x09)) as u16 + 2000; // assuming 20xx

        DateTime { second, minute, hour, day, month, year }
    }
    fn read_register(reg: u8) -> u8 {
        unsafe {
            asm!("out 0x70, al", in("al") reg);
            let mut val: u8;
            asm!("in al, 0x71", out("al") val);
            val
        }
    }
    fn bcd_to_bin(val: u8) -> u8 {
        (val & 0x0F) + ((val >> 4) * 10)
    }
}