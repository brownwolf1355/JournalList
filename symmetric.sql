/*
 * JournalList sql script to process webcrawler.py output.
 *
 * Copyright (c) 2021 Brown Wolf Consulting LLC
 * License: Creative Commons Attribution-NonCommercial-ShareAlike license. See: https://creativecommons.org/
 *
 * Generate intermediate tables
 *
 */
insert into member_list (srcurl,attr,refurl) select * from trust_txt where attr = "member" order by srcurl, refurl, attr asc;
insert into member_count (srcurl,count) select srcurl, count(*) from member_list group by srcurl;
insert into belongto_list (srcurl,attr,refurl) select * from trust_txt where attr = "belongto" order by srcurl, refurl, attr asc;
insert into belongto_count (srcurl,count) select srcurl, count(*) from belongto_list group by srcurl;
insert into control_list (srcurl,attr,refurl) select * from trust_txt where attr = "control" and srcurl != refurl order by srcurl, refurl, attr asc;
insert into controlledby_list (srcurl,attr,refurl) select * from trust_txt where attr = "controlledby" and srcurl != refurl order by srcurl, refurl, attr asc;
insert into vendor_list (srcurl,attr,refurl) select * from trust_txt where attr = "vendor" order by srcurl, refurl, attr asc;
insert into customer_list (srcurl,attr,refurl) select * from trust_txt where attr = "customer" order by srcurl, refurl, attr asc;
/*
 * Generate the list of symmetric links, where:
 *   member_list.refurl = belongto_list.srcurl and belongto_list.refurl = member_list.srcurl or
 *   control_list.refurl = controlledby_list.srcurl and controlledby_list.refurl = control_list.srcurl or 
 *   vendor_list.refurl = customer_list.srcurl and customer_list.refurl = vendor_list.srcurl
 *
 */
insert into symmetric_list (srcurl1,attr1,refurl1,srcurl2,attr2,refurl2) select distinct * from member_list join belongto_list on member_list.refurl = belongto_list.srcurl and belongto_list.refurl = member_list.srcurl;
insert into symmetric_list (srcurl1,attr1,refurl1,srcurl2,attr2,refurl2) select distinct * from control_list join controlledby_list on control_list.refurl = controlledby_list.srcurl and controlledby_list.refurl = control_list.srcurl;
insert into symmetric_list (srcurl1,attr1,refurl1,srcurl2,attr2,refurl2) select distinct * from vendor_list join customer_list on vendor_list.refurl = customer_list.srcurl and customer_list.refurl = vendor_list.srcurl;
/*
 * Generate the list of asymmetric links, where: the refurl matches the refurl on an HTTP GET error.
 *
 */
insert into asymmetric_list (srcurl,attr,refurl) select trust_txt.srcurl, trust_txt.attr, trust_txt.refurl from trust_txt join http_errors where trust_txt.refurl = http_errors.refurl;
/*
 * Generate the list of associations, publishers, and vendors.
 *
 * Associations = srcurl of any that contain "member" attributes, refurl of any that contain "belongto" attributes, and any refurls they control (Only associations have members, publishers and vendors do not)
 * Vendors = srcurl of any that contain "customer" attributes, any refurls that contain "vendor" attributes, and any refurls they control (Only vendors have customers or are vendors)
 * Publishers = srcurl of any that contain "belongto" attributes and are not associations or vendors, any refurls that contain "member" attributes and are not associations or vendors, and any refurls they control
 * 
 */
insert into temp_list (srcurl) select distinct srcurl from member_list;
insert into temp_list (srcurl) select distinct refurl from belongto_list;
insert into temp_list (srcurl) select distinct refurl from control_list join temp_list where control_list.srcurl = temp_list.srcurl;
insert into associations_list (srcurl) select distinct srcurl from temp_list order by srcurl;
delete from temp_list where srcurl is not null;
#
insert into temp_list (srcurl) select distinct srcurl from customer_list;
insert into temp_list (srcurl) select distinct refurl from vendor_list;
insert into temp_list (srcurl) select distinct refurl from control_list join temp_list where control_list.srcurl = temp_list.srcurl;
insert into vendors_list (srcurl) select distinct temp_list.srcurl from temp_list;
delete from temp_list where srcurl is not null;
#
insert into temp_list (srcurl) select distinct srcurl from belongto_list;
insert into temp_list (srcurl) select distinct refurl from member_list;
insert into temp_list (srcurl) select distinct refurl from control_list join temp_list where control_list.srcurl = temp_list.srcurl;
insert into publishers_list (srcurl) select distinct temp_list.srcurl from temp_list where (temp_list.srcurl not in (select associations_list.srcurl from associations_list) and temp_list.srcurl not in (select vendors_list.srcurl from vendors_list)) order by temp_list.srcurl;
delete from temp_list where srcurl is not null;
#
/*
 * Generate the list of urls that are controlled by the associations, publishers, and vendors
 *
 */
insert into controlled_list (srcurl) select distinct refurl from control_list;
insert into controlled_list (srcurl) select distinct srcurl from controlledby_list;
/*
 * Generate the statistics for associations, publishers, vendors, JournalList members, symmetric and asymmetric relationships.
 *
 */
insert into stats (title) values ("Number of Associations");
update stats set count = (select count (distinct srcurl) from associations_list) where count is null;
insert into stats (title) values ("Number of Publishers");
update stats set count = (select count (distinct srcurl) from publishers_list) where count is null;
insert into stats (title) values ("Number of Vendors");
insert into stats (title,count) values ("Ecosystem Total",0);
update stats set count = (select count (distinct srcurl) from vendors_list) where count is null;
insert into stats (title) values ("Number of Association Members of JournalList");
update stats set count = (select count (distinct associations_list.srcurl) from associations_list join member_list where associations_list.srcurl = member_list.refurl and member_list.srcurl = "https://www.journallist.net/") where count is null;
insert into stats (title) values ("Number of Publisher Members of JournalList");
update stats set count = (select count (distinct publishers_list.srcurl) from publishers_list join member_list where publishers_list.srcurl = member_list.refurl and member_list.srcurl = "https://www.journallist.net/") where count is null;
insert into stats (title) values ("Number of Vendor Members of JournalList");
update stats set count = (select count (distinct vendors_list.srcurl) from vendors_list join member_list where vendors_list.srcurl = member_list.refurl and member_list.srcurl = "https://www.journallist.net/") where count is null;
insert into stats (title,count) values ("JournalList Total",0);
insert into stats (title) values ("Number of trust.txt files Found");
update stats set count = (select count (distinct srcurl) from trust_txt) where count is null;
insert into stats (title) values ("Number of Symmetric Relationships");
update stats set count = (select count (srcurl1) from symmetric_list) where count is null;
insert into stats (title) values ("Number of Asymmetric Relationships");
update stats set count = (select count (srcurl) from asymmetric_list) where count is null;
