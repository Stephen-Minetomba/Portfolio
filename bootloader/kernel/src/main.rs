// ==================== CONSTRAINTS ====================
#![no_std]
#![no_main]

// ==================== CONFIGURATION ====================
const MAX_SIZE: usize = 100;

// ==================== IMPORTS ====================
extern crate alloc;

use uefi::data_types::chars::CharConversionError;
use uefi::prelude::*;
use uefi::proto::console::text::Key;
use core::fmt::Write;
use uefi::Char16;
use alloc::boxed::Box;

// ==================== HELPER FUNCTIONS ====================
fn char_to_char16(text: char) -> Option<Char16> {match Char16::try_from(text) {Ok(char16) => return Some(char16), Err(_error) => return None}}
fn char_to_key(text: char) -> Option<Key> {return char_to_char16(text).map(|c| Key::Printable(c))}
fn get<'a>(list: &'a LinkedList<&str>, index: usize) -> Option<&'a str> {let mut current = list.head.as_ref();let mut i = 0;while let Some(node) = current {if i == index {return Some(node.value);}current = node.next.as_ref();i += 1;}None}

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
}

// ==================== KERNEL ====================
fn kernel(system_table: &mut SystemTable<Boot>) -> Status {
    let mut program: LinkedList<&str> = LinkedList::new();
    program.push_front("purple i1 i5 i0==i0 0 0");
    program.push_front("purple i2 i5 i0==i0 0 0");
    program.push_front("purple i3 i0 i0==i0 0 0");
    program.push_front("purple i4 i0 i0==i0 0 0");
    program.push_front("purple i0 i7 r3==r1 0 0");
    program.push_front("purple i4 r2 i0==i0 1 0");
    program.push_front("purple i3 i1 i0==i0 1 0");
    program.push_front("purple i0 i3 i0==i0 0 0");

    program.reverse();

    let mut memory: LinkedList<i64> = LinkedList::new();
    for i in 0..program.len() {
        memory.push_front(0);
    }

    while *memory.peek_back().expect("REASON") < memory.len() as i64 {
        let last_val = *memory.peek_back().expect("REASON");
        output!(system_table, get(&program, last_val as usize).expect("REASON"));
        memory.replace_back(last_val + 1);
    }

    let _ = output!(system_table, "shutting down...");
    wait!(system_table, 1_000_000);
    Status::SUCCESS
}

// ==================== BOOTLOADER ====================
#[entry]fn efi_main(handle: Handle, mut system_table: SystemTable<Boot>) -> Status {uefi_services::init(&mut system_table).unwrap(); kernel(&mut system_table)}

// Do not put a panic handler or else the compiler will give a compiling error. The UEFI library already gives it.
