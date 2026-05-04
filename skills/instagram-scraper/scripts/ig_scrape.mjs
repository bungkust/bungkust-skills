#!/usr/bin/env node
/**
 * General Instagram Scraper
 * Usage: node ig_scrape.mjs --user USERNAME --cookie "COOKIE" [--amount N] [--save-images] [--ocr]
 */

import { igApi } from 'insta-fetcher';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { spawnSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = '/tmp/ig_scrape';

// Parse args
const args = process.argv.slice(2);
let username = '';
let cookie = '';
let amount = 5;
let saveImages = false;
let doOcr = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--user') username = args[++i];
  else if (args[i] === '--cookie') cookie = args[++i];
  else if (args[i] === '--amount') amount = parseInt(args[++i]);
  else if (args[i] === '--save-images') saveImages = true;
  else if (args[i] === '--ocr') doOcr = true;
}

if (!username || !cookie) {
  console.log('Usage: node ig_scrape.mjs --user USERNAME --cookie "COOKIE" [--amount N] [--save-images] [--ocr]');
  process.exit(1);
}

function run(cmd, args_arr) {
  const r = spawnSync(cmd, args_arr, { encoding: 'utf-8', maxBuffer: 1024*1024 });
  return (r.stdout || '') + (r.stderr || '');
}

function ocrImage(imgPath) {
  const pngPath = imgPath.replace(/\.(jpg|jpeg|png)$/i, '_ocr.png');
  run('ffmpeg', ['-i', imgPath, '-q:v', '3', pngPath, '-y']);
  return run('tesseract', [pngPath, 'stdout', '2>/dev/null']);
}

async function main() {
  console.log(`🔍 Fetching @${username} — ${amount} posts...\n`);

  const ig = new igApi(cookie, {
    userAgent: 'Instagram 270.0.0.0.0 Android (24/7.0; 320dpi; 720x1280; samsung; SM-G930F; herolte; samsunge; en_US)'
  });

  let posts;
  try {
    const res = await ig.fetchUserPostsV2(username, '', amount);
    posts = res.items;
  } catch(e) {
    console.error('❌ Fetch error:', e.message);
    console.error('   Response:', e.response?.data || 'no response');
    process.exit(1);
  }

  if (!posts || posts.length === 0) {
    console.error('❌ No posts found');
    process.exit(1);
  }

  const results = [];

  for (const item of posts) {
    const node = item.node || item;
    const shortcode = node.code || '';
    // Get timestamp — Android API uses taken_at, web uses taken_at_timestamp
    const ts = node.taken_at || node.taken_at_timestamp;
    const timestamp = ts ? new Date(ts * (ts > 1e12 ? 1 : 1000)) : null;
    const caption = node.caption?.text || '';
    const likes = node.likes_count || 0;
    const comments = node.comments_count || 0;

    // Get images
    let images = [];
    if (node.carousel_media?.length > 0) {
      images = node.carousel_media
        .map(m => m.image_versions2?.candidates?.[0]?.url)
        .filter(Boolean);
    } else if (node.image_versions2?.candidates?.[0]?.url) {
      images = [node.image_versions2.candidates[0].url];
    }

    let ocrText = '';
    if ((saveImages || doOcr) && images.length > 0) {
      const userDir = `${OUT_DIR}/${username}/${shortcode}`;
      mkdirSync(userDir, { recursive: true });

      const imgTexts = [];
      for (let i = 0; i < images.length; i++) {
        const imgPath = `${userDir}/img_${i}.jpg`;
        
        if (saveImages) {
          run('bash', ['-c', `curl -s -L "${images[i]}" -o "${imgPath}"`]);
        }

        if (doOcr) {
          if (!existsSync(imgPath)) {
            run('bash', ['-c', `curl -s -L "${images[i]}" -o "${imgPath}"`]);
          }
          const text = ocrImage(imgPath);
          if (text.trim()) imgTexts.push(text.trim());
        }
      }
      ocrText = imgTexts.join('\n---\n');
    }

    const post = {
      shortcode,
      taken_at: timestamp ? timestamp.toISOString() : null,
      date_str: timestamp ? timestamp.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' }) : null,
      caption,
      likes,
      comments,
      images,
      is_carousel: (node.carousel_media?.length || 0) > 1,
      ocr_text: ocrText || undefined,
    };

    results.push(post);

    // Print summary
    console.log(`📄 ${shortcode}`);
    console.log(`   ${post.date_str || '?'} | ❤️ ${likes} | 💬 ${comments}`);
    if (caption) console.log(`   Caption: ${caption.substring(0, 80)}${caption.length > 80 ? '...' : ''}`);
    if (images.length > 0) console.log(`   Images: ${images.length} (${post.is_carousel ? 'carousel' : 'single'})`);
    if (ocrText) console.log(`   OCR: ${ocrText.substring(0, 100)}...`);
    console.log('');
  }

  // Save JSON output
  const out = {
    username,
    fetched_at: new Date().toISOString(),
    post_count: results.length,
    posts: results,
  };

  const outFile = `${OUT_DIR}/${username}_${Date.now()}.json`;
  mkdirSync(path.dirname(outFile), { recursive: true });
  writeFileSync(outFile, JSON.stringify(out, null, 2));
  console.log(`💾 Output: ${outFile}`);
  console.log(`✅ Done! Got ${results.length} posts`);
}

main().catch(e => {
  console.error('❌ Error:', e.message);
  process.exit(1);
});
