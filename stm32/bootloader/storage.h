/*
 * (c) Copyright 2018 by Coinkite Inc. This file is part of Coldcard <coldcardwallet.com>
 * and is covered by GPLv3 license found in COPYING.
 */
#pragma once

#include "basics.h"
#include "stm32l4xx_hal.h"

// Details of the OTP area. 64-bit slots.
#define OPT_FLASH_BASE     0x1FFF7000
#define NUM_OPT_SLOTS      128

// This is what we're keeping secret... Kept in flash, written mostly once.
// fields must be 64-bit aligned so they can be written independantly
typedef struct {
    // Piaring secret: picked once at factory when turned on
    // for the first time. Crypto-tied into all the secrets of the ATECC508A on the
    // same board.
    //
    uint8_t pairing_secret[32];
    uint8_t pairing_secret_xor[32];
    uint64_t ae_serial_number[2];      // 9 bytes active
    uint8_t  bag_number[32];           // 32 bytes max, zero padded string
} rom_secrets_t;

// This area is defined in linker script as last page of boot loader flash.
// == 0x7800
#define rom_secrets         ((rom_secrets_t *)BL_NVROM_BASE)

// Call at boot time. Picks pairing secret and/or verifies it.
void flash_setup(void);

// Set option-bytes region to appropriate values
void flash_lockdown_hard(uint8_t rdp_level_code);

// Save a serial number from secure element
void flash_save_ae_serial(const uint8_t serial[9]);

// Write bag number (probably a string)
void flash_save_bag_number(const uint8_t new_number[32]);

// Are we operating in level2?
static inline bool flash_is_security_level2(void) {
    return ((FLASH->OPTR & FLASH_OPTR_RDP_Msk) == 0xCC);
}

// We store some values in the RTC "backup" registers
// - these are protected against accidental writes
// - not cleared by system reset, full power cycle required
// - mpy code could still change, so not secure.
// - kinda pointless, but I have no SRAM that isn't wiped at boot
// - XXX not working! no clock maybe? Reads as zero.

#define IDX_WORD_LOOKUPS_USED               0x0
#define IDX_DURESS_LASTGOOD_1               0x1
#define IDX_DURESS_LASTGOOD_2               0x2

uint32_t backup_data_get(int idx);
void backup_data_set(int idx, uint32_t new_value);


// generial purpose flash functions
void flash_setup0(void);
void flash_lock(void);
void flash_unlock(void);
int flash_burn(uint32_t address, uint64_t val);
int flash_page_erase(uint32_t address);

// write to OTP
int record_highwater_version(const uint8_t timestamp[8]);

// EOF
