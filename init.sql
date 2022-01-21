/*
 * init.sql - JournalList SQLite webcrawl sqlite3 init script
 *
 * Copyright (c) 2021 Brown Wolf Consulting LLC
 * License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
 *
 * Create intermediate tables: list and count by attribute.
 *
 */
CREATE TABLE member_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE belongto_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE control_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE controlledby_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE vendor_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE customer_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
/*
 * Create output tables: symmetric links, list of associations, publishers, vendors, and controlled urls, and statistics.
 *
 */
CREATE TABLE symmetric_list ("srcurl1" TEXT, "attr1" TEXT, "refurl1" TEXT, "srcurl2" TEXT, "attr2" TEXT, "refurl2" TEXT);
CREATE TABLE asymmetric_list ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE associations_list ("srcurl" TEXT);
CREATE TABLE publishers_list ("srcurl" TEXT);
CREATE TABLE vendors_list ("srcurl" TEXT);
CREATE TABLE controlled_list ("srcurl" TEXT);
CREATE TABLE control_dups ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE controlledby_dups ("srcurl" TEXT, "attr" TEXT, "refurl" TEXT);
CREATE TABLE temp_list ("srcurl" TEXT);
create table stats ("title" TEXT, "count" INTEGER);
/*
 * Set mode and turn headers on.
 *
 */
.mode csv
.headers on
