#!/usr/bin/env node
/**
 * Heartopia Daily Scraper
 * Fetches latest Update Harian from @myheartopia.id, OCR images, update vault
 * 
 * Usage: node scrape_heartopia.mjs
 */

import { igApi } from 'insta-fetcher';
import { writeFileSync, readFileSync, existsSync, appendFileSync, mkdirSync } from 'fs';
import { spawnSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORK_DIR = '/tmp/heartopia-scrape';
const VAULT_PATH = '/root/obsidian-vault/10-Projects/Pribadi/Heartopia-Daily-Tracker.md';

// Cookie from browser (Instagram) — UPDATE this if session expires
const COOKIE_STR = 'csrftoken=h8LEeebaRTTZO5poFLZe8xUUU2v4Ysng; sessionid=76660013529%3A90HYFuvCoL9HCs%3A19%3AAYjerQB3CBcfX42Nx6R1PHardpTH9Yo5qpyR4Ewqzw; mid=aBGLugAEAAFNTkkwC6Bz6UIa1c19; ig_did=9F5CACBE-E200-4E35-A065-D54551321712; datr=LE5CaPlFqGltzXzOgpB2Oqgx; ds_user_id=76660013529; ig_nrcb=1; ps_l=1; ps_n=1; dpr=1; wd=1519x1060';

function run(cmd, args) {
  const r = spawnSync(cmd, args, { encoding: 'utf-8', maxBuffer: 1024*1024 });
  return (r.stdout || '') + (r.stderr || '');
}

function ocrImage(imgPath) {
  const pngPath = imgPath.replace(/\.(jpg|jpeg|png)$/i, '_ocr.png');
  // Convert to PNG
  run('ffmpeg', ['-i', imgPath, '-q:v', '3', pngPath, '-y']);
  // OCR
  const out = run('tesseract', [pngPath, 'stdout', '2>/dev/null']);
  return out;
}

function parseOcrText(text) {
  const result = {};
  
  // Date pattern: "Sabtu, 2 Mei 2026" or "2 Mei 2026"
  const dateMatch = text.match(/(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)[,.]?\s*(\d+)\s*(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s*(\d{4})/i)
    || text.match(/(\d+)\s*(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s*(\d{4})/i);
  if (dateMatch) result.date = dateMatch[0];
  
  // Oak Tree: "Oak Tree: Rumah No. X" or "🌳 Oak Tree: ..."
  const oakMatch = text.match(/Oak\s*Tree:?\s*Rumah\s*No\.?\s*(\d+)/i);
  if (oakMatch) result.oakTree = `Rumah No. ${oakMatch[1]}`;
  
  // Fluorite: "Fluorite: Rumah No. X" or "💎 Fluorite: ..."
  const fluoriteMatch = text.match(/Fluorite:?\s*Rumah\s*No\.?\s*(\d+)/i);
  if (fluoriteMatch) result.fluorite = `Rumah No. ${fluoriteMatch[1]}`;
  
  // Cuaca: "Akan HUJAN", "CERAH", "Mendung", etc.
  if (/HUJAN/i.test(text)) result.cuaca = 'HUJAN';
  else if (/CERAH/i.test(text)) result.cuaca = 'CERAH';
  else if (/MENDUNG/i.test(text) || /MENDUNG/i.test(text)) result.cuaca = 'MENDUNG';
  else if (/OFFLINE/i.test(text)) result.cuaca = 'OFFLINE';
  else if (/Hujan\s+Ringan/i.test(text)) result.cuaca = 'Hujan Ringan';
  
  // Dory's items: "Barang Jualannya:", then item names
  // Pattern: ItemName (price) — prices are 150, 200, 80, etc.
  // Clean OCR artifacts: remove @copyright lines, stray chars
  const cleanedText = text
    .replace(/©.*$/gm, '')
    .replace(/@\w+/g, '')
    .replace(/\$\d+/g, '')
    .replace(/\b\d{2,3}\b/g, '')
    .replace(/wr|S\|/gi, '')
    .trim();
  
  const doryMatch = cleanedText.match(/Barang\s*Jualannya?:?\s*([A-Za-z\s]+?)(?=\s{2,}|$)/i);
  if (doryMatch) {
    const items = doryMatch[1]
      .split(/\s{2,}/)
      .map(s => s.trim())
      .filter(s => s.length > 1 && /[a-zA-Z]{2,}/.test(s));
    result.doryItems = items.join(', ');
  }
  
  // Time info: "pukul XX.XX" or "jam XX"
  const timeMatch = text.match(/(pukul|jam)\s*(\d{1,2})[.:]?(\d{2})?/i);
  if (timeMatch) result.time = `${timeMatch[2]}:${timeMatch[3] || '00'}`;
  
  // Events: keywords like "Event:", "Mini Event", "Collaboration"
  if (/Mini\s*Event/i.test(text)) result.events = 'Mini Event';
  if (/Collaboration/i.test(text)) result.events = (result.events || '') + ' Collaboration';
  
  return result;
}

async function main() {
  console.log('🔍 Starting Heartopia Daily Scrape...\n');
  
  // Init Instagram
  const ig = new igApi(COOKIE_STR, {
    userAgent: 'Instagram 270.0.0.0.0 Android (24/7.0; 320dpi; 720x1280; samsung; SM-G930F; herolte; samsunge; en_US)'
  });
  
  // Fetch posts from @myheartopia.id
  console.log('📱 Fetching posts from @myheartopia.id...');
  let posts;
  try {
    const res = await ig.fetchUserPostsV2('myheartopia.id', '', 10);
    posts = res.items;
  } catch(e) {
    console.error('❌ Failed to fetch posts:', e.message);
    process.exit(1);
  }
  
  if (!posts || posts.length === 0) {
    console.error('❌ No posts found');
    process.exit(1);
  }
  
  // Find "Update Harian" post
  // posts are in {node: {...}} format from fetchUserPostsV2
  let updatePost = null;
  let postDate = null;
  
  for (const item of posts) {
    const node = item.node || item;
    const caption = node.caption?.text || '';
    const shortcode = node.code || '';
    
    if (/Update\s*Harian/i.test(caption) || /update\s*harian/i.test(caption)) {
      updatePost = node;
      postDate = node.taken_at_timestamp ? new Date(node.taken_at_timestamp * 1000) : null;
      console.log(`✅ Found Update Harian post: ${shortcode}`);
      if (postDate) console.log(`   Date: ${postDate.toISOString().split('T')[0]}`);
      break;
    }
  }
  
  if (!updatePost) {
    // Fallback: use latest post
    const latest = posts[0].node || posts[0];
    updatePost = latest;
    postDate = latest.taken_at_timestamp ? new Date(latest.taken_at_timestamp * 1000) : new Date();
    console.log('⚠️ No "Update Harian" found, using latest post');
  }
  
  // Get images (carousel or single)
  const carouselMedia = updatePost.carousel_media || [];
  const hasCarousel = carouselMedia.length > 0;
  
  let imageUrls = [];
  if (hasCarousel) {
    imageUrls = carouselMedia.map(m => m.image_versions2?.candidates?.[0]?.url).filter(Boolean);
  } else {
    const singleUrl = updatePost.image_versions2?.candidates?.[0]?.url;
    if (singleUrl) imageUrls = [singleUrl];
  }
  
  console.log(`\n📸 Found ${imageUrls.length} image(s)`);
  
  // Download + OCR each image
  mkdirSync(`${WORK_DIR}/ocr`, { recursive: true });
  const ocrResults = [];
  
  for (let i = 0; i < imageUrls.length; i++) {
    const url = imageUrls[i];
    const imgPath = `${WORK_DIR}/ocr/img_${i}.jpg`;
    
    console.log(`\n⬇️  Downloading image ${i+1}...`);
    const curlCmd = `curl -s -L "${url}" -o "${imgPath}"`;
    await run('bash', ['-c', curlCmd]);
    
    if (!existsSync(imgPath)) {
      console.log(`   ❌ Failed to download`);
      continue;
    }
    
    console.log(`   🔍 Running OCR...`);
    const ocrText = String(ocrImage(imgPath));
    console.log(`   OCR Output:\n${ocrText.substring(0, 500)}`);
    
    ocrResults.push({ index: i, text: ocrText });
  }
  
  // Parse all OCR results
  console.log('\n📋 Parsing results...');
  const parsed = ocrResults.map(r => parseOcrText(r.text));
  const merged = Object.assign({}, ...parsed);
  
  console.log('\n=== PARSED DATA ===');
  console.log(JSON.stringify(merged, null, 2));
  
  // Format vault entry
  const now = postDate || new Date();
  const dayNames = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
  const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
  const dayName = dayNames[now.getDay()];
  const day = now.getDate();
  const month = monthNames[now.getMonth()];
  const year = now.getFullYear();
  const dateStr = `${dayName}, ${day} ${month} ${year}`;
  
  const entryLines = [
    `## ${dateStr}`,
    ``,
    `**Cuaca:** ${merged.cuaca || '-'}`,
    `**Oak Tree:** ${merged.oakTree || '-'}`,
    `**Fluorite:** ${merged.fluorite || '-'}`,
  ];
  
  if (merged.doryItems) {
    entryLines.push(`**Dory (saat hujan):** ${merged.doryItems}`);
  }
  if (merged.events) {
    entryLines.push(`**Events:** ${merged.events}`);
  }
  if (merged.time) {
    entryLines.push(`**Jam:** ${merged.time}`);
  }
  entryLines.push('');
  
  const entry = entryLines.join('\n');
  console.log('\n=== VAULT ENTRY ===');
  console.log(entry);
  
  // Check if entry already exists for this date
  const vaultContent = existsSync(VAULT_PATH) ? readFileSync(VAULT_PATH, 'utf-8') : '';
  const datePattern = new RegExp(`## ${dayName},\\s*${day}\\s*${month}\\s*${year}`);
  
  if (datePattern.test(vaultContent)) {
    console.log('\n⚠️ Entry for today already exists in vault. Skipping update.');
    console.log('To force update, remove the existing entry first.');
    process.exit(0);
  }
  
  // Append to vault
  appendFileSync(VAULT_PATH, '\n' + entry);
  console.log('\n✅ Updated vault:', VAULT_PATH);
  
  // Git commit
  const gitDir = path.dirname(VAULT_PATH);
  run('bash', ['-c', `cd ${gitDir} && git add -A && git commit -m "heartopia update: ${dateStr}" 2>/dev/null`]);
  
  console.log('\n✅ Done!');
}

main().catch(e => {
  console.error('❌ Error:', e);
  process.exit(1);
});
