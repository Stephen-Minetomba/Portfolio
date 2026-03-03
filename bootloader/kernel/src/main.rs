// ==================== CONSTRAINTS ====================
#![no_std]
#![no_main]

// ==================== IMPORTS ====================
extern crate alloc;

use uefi::data_types::chars::CharConversionError;
use uefi::prelude::*;
use uefi::proto::console::text::Key;
use core::fmt::Write;
use uefi::Char16;
use alloc::boxed::Box;
use crate::alloc::string::ToString;
use alloc::vec::Vec;
use core::mem;

// ==================== HELPER FUNCTIONS ====================
fn char_to_char16(text: char) -> Option<Char16> {match Char16::try_from(text) {Ok(char16) => return Some(char16), Err(_error) => return None}}
fn char_to_key(text: char) -> Option<Key> {return char_to_char16(text).map(|c| Key::Printable(c))}
fn get<'a, T>(list: &'a LinkedList<T>, index: usize) -> Option<&'a T> {
    let mut current = list.head.as_ref();
    let mut i = 0;
    while let Some(node) = current {
        if i == index {
            return Some(&node.value);
        }
        current = node.next.as_ref();
        i += 1;
    }
    None
}
fn resolve(
    ri1_str: &str,
    memory: &LinkedList<i64>,
) -> Option<i64> {
    let first_char = ri1_str.chars().next()?;
    if first_char.eq_ignore_ascii_case(&'r') {
        let idx = ri1_str[1..].parse::<usize>().ok();
        get(memory, idx.unwrap()).copied()
    } else if first_char.eq_ignore_ascii_case(&'i') {
        ri1_str[1..].parse::<i64>().ok()
    } else {
        None
    }
}
fn evaluate(cond: &str, memory: &LinkedList<i64>) -> Option<bool> {
    let operators = ["==", "!=", ">=", "<=", ">", "<"];
    let mut op_found = None;
    for &op in &operators {
        if cond.contains(op) {
            op_found = Some(op);
            break;
        }
    }
    let op = op_found?;
    let parts: Vec<&str> = cond.split(op).collect();
    if parts.len() != 2 {
        return None;
    }
    let left_raw = parts[0].trim();
    let right_raw = parts[1].trim();
    let left = resolve(left_raw, memory)?;
    let right = resolve(right_raw, memory)?;
    let result = match op {
        "==" => left == right,
        "!=" => left != right,
        ">"  => left > right,
        "<"  => left < right,
        ">=" => left >= right,
        "<=" => left <= right,
        _    => return None,
    };
    Some(result)
}

// ==================== MACROS ====================
macro_rules! wait {($system_table:expr, $microseconds:expr) => {$system_table.boot_services().stall($microseconds)};}
macro_rules! clear {($system_table:expr) => {$system_table.stdout().clear()};}
macro_rules! output {($system_table:expr, $text:expr) => {$system_table.stdout().write_str($text)};}
macro_rules! input {($system_table:expr) => {$system_table.stdin().read_key().ok().flatten()};}
macro_rules! is_pressed {($system_table:expr, $key:expr) => {$system_table.stdin().read_key().ok().flatten() == char_to_key($key)};}

// ==================== MEMORY ====================
struct Node<T> {value: T,next: Option<Box<Node<T>>>,}
pub struct LinkedList<T> {head: Option<Box<Node<T>>>,length: usize,}
impl<T> LinkedList<T> {
    pub fn new() -> Self {LinkedList {head: None,length: 0,}}
    pub fn push_front(&mut self, value: T) {let new_node = Box::new(Node {value,next: self.head.take(),});self.head = Some(new_node);self.length += 1;}
    pub fn pop_front(&mut self) -> T {self.head.take().map(|node| {self.head = node.next;self.length -= 1;node.value}).expect("pop_front called on empty list")}
    pub fn len(&self) -> usize {self.length}
    pub fn is_empty(&self) -> bool {self.head.is_none()}
    pub fn peek_front(&self) -> Option<&T> {self.head.as_ref().map(|node| &node.value)}
    pub fn peek_front_mut(&mut self) -> Option<&mut T> {self.head.as_mut().map(|node| &mut node.value)}
    pub fn peek_back(&self) -> Option<&T> {let mut current = self.head.as_ref();while let Some(node) = current {if node.next.is_none() {return Some(&node.value);}current = node.next.as_ref();}None}
    pub fn replace_back(&mut self, new_value: T) -> Option<T> {let mut current = self.head.as_mut();while let Some(node) = current {if node.next.is_none() {let old_value = core::mem::replace(&mut node.value, new_value);return Some(old_value);}current = node.next.as_mut();}None}
    pub fn reverse(&mut self) {let mut prev: Option<Box<Node<T>>> = None;let mut current = self.head.take();while let Some(mut node) = current {let next = node.next.take();node.next = prev;prev = Some(node);current = next;}self.head = prev;}
    pub fn replace(&mut self, index: usize, new_value: T) -> Option<T> {let mut current = self.head.as_mut();let mut i = 0;while let Some(node) = current {if i == index {let old_value = core::mem::replace(&mut node.value, new_value);return Some(old_value);}current = node.next.as_mut();i += 1;}None}
}

// ==================== KERNEL ====================
fn kernel(system_table: &mut SystemTable<Boot>) -> Status {
    let mut program: LinkedList<&str> = LinkedList::new();

    program.push_front("purple i1 i5 i0==i0 0 0");
    program.push_front("purple i2 i3 i0==i0 0 0");
    program.push_front("purple i0 i4 r3!=r2 0 0");
    program.push_front("purple i4 r1 i0==i0 1 0");
    program.push_front("purple i3 i1 i0==i0 1 0");
    program.push_front("purple i0 i2 r3!=r2 0 0");
    program.push_front("print-value r0");
    program.push_front("print-ascii i10");
    program.push_front("print-value r1");
    program.push_front("print-ascii i10");
    program.push_front("print-value r2");
    program.push_front("print-ascii i10");
    program.push_front("print-value r3");
    program.push_front("print-ascii i10");
    program.push_front("print-value r4");
    program.push_front("print-ascii i10");

    program.reverse();

    let mut memory: LinkedList<i64> = LinkedList::new();
    for _i in 0..program.len() {
        memory.push_front(0);
    }

    while *get(&memory, 0).unwrap() < program.len() as i64 {
        let instruction = get(&program, *get(&memory, 0).unwrap() as usize).unwrap();
        
        // Python equivalent: instruction_memory = instruction.split(" ")
        let mut instruction_memory: LinkedList<&str> = LinkedList::new();
        let mut start = 0;
        let bytes = instruction.as_bytes();
        for i in 0..bytes.len() {
            if bytes[i] == b' ' {
                if start != i {
                    let part = &instruction[start..i];
                    instruction_memory.push_front(part);
                }
                start = i + 1;
            }
        }
        if start < instruction.len() {
            instruction_memory.push_front(&instruction[start..]);
        }
        instruction_memory.reverse();

        if instruction_memory.len() == 6 {
            let ri1 = resolve(get(&instruction_memory, 1).unwrap(), &memory).unwrap();
            let mut ri2 = resolve(get(&instruction_memory, 2).unwrap(), &memory).unwrap();
            let c3 = get(&instruction_memory, 3).unwrap();
            let i4 = get(&instruction_memory, 4).unwrap().parse::<i64>().ok().unwrap();
            let i5 = get(&instruction_memory, 5).unwrap().parse::<i64>().ok().unwrap();
            if i5 == 1 {
                ri2 *= -1;
            }
            if evaluate(&c3.to_string(), &memory).unwrap() {
                if i4 == 1 {
                    let _ = memory.replace(ri1 as usize, get(&memory, ri1 as usize).unwrap() + ri2);
                }else if i4 == 0 {
                    let _ = memory.replace(ri1 as usize, ri2);
                }
            }
        } else if instruction_memory.len() == 2 {
            // a few instructions for I/O
            if get(&instruction_memory, 0) == Some(&&"print-ascii") {
                let _ = output!(system_table, core::str::from_utf8(&[resolve(get(&instruction_memory, 1).unwrap(), &memory).unwrap() as u8 as char as u8]).unwrap());
            }
            if get(&instruction_memory, 0) == Some(&&"print-value") {
                let _ = output!(system_table, &resolve(get(&instruction_memory, 1).unwrap(), &memory).unwrap().to_string());
            }
        } else {
            let _ = output!(system_table, "WARNING! Program length is invalid. Actual program length:\n");
            let _ = output!(system_table, &instruction.len().to_string());
            let _ = output!(system_table, "\n");
        }
        
        memory.replace(0, get(&memory, 0).unwrap() + 1);
    }

    let _ = output!(system_table, "shutting down...");
    wait!(system_table, 1_000_000);
    Status::SUCCESS
}

// ==================== BOOTLOADER ====================
#[entry]fn efi_main(handle: Handle, mut system_table: SystemTable<Boot>) -> Status {uefi_services::init(&mut system_table).unwrap(); kernel(&mut system_table)}

// Do not put a panic handler or else the compiler will give a compiling error. The UEFI library already gives it.