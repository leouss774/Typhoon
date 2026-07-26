import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { randomUUID } from 'crypto';

const router = new Hono();

const ALLOWED_TYPES = [
  'image/jpeg', 'image/png', 'image/gif', 'image/webp',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

const MAX_SIZE = 20 * 1024 * 1024; // 20 MB

/**
 * POST /api/upload
 * Upload files for a property. Accepts multipart/form-data.
 * Fields: files (multiple), propertyId (string)
 */
router.post('/', async (c) => {
  try {
    const body = await c.req.parseBody();
    const files = body['files'];
    const propertyId = body['propertyId'] as string | undefined;

    const fileArray = Array.isArray(files) ? files : (files ? [files] : []);

    if (fileArray.length === 0) {
      return c.json({ error: 'Aucun fichier fourni' }, 400);
    }

    const uploadsDir = join(process.cwd(), 'uploads');
    await mkdir(uploadsDir, { recursive: true });

    const uploaded: Array<{
      originalName: string;
      filename: string;
      size: number;
      mimeType: string;
      path: string;
    }> = [];

    for (const file of fileArray) {
      if (!(file instanceof File)) continue;

      if (!ALLOWED_TYPES.includes(file.type)) {
        return c.json({ error: `Format non supporté: ${file.type}` }, 400);
      }

      if (file.size > MAX_SIZE) {
        return c.json({ error: `Fichier trop volumineux: ${file.name} (max 20 Mo)` }, 400);
      }

      const ext = file.name.split('.').pop() || 'bin';
      const filename = `${Date.now()}-${randomUUID().slice(0, 8)}.${ext}`;
      const filepath = join(uploadsDir, filename);
      const buffer = await file.arrayBuffer();
      await writeFile(filepath, Buffer.from(buffer));

      uploaded.push({
        originalName: file.name,
        filename,
        size: file.size,
        mimeType: file.type,
        path: `/uploads/${filename}`,
      });
    }

    return c.json({
      success: true,
      files: uploaded,
      propertyId: propertyId || null,
      message: `${uploaded.length} fichier(s) uploadé(s) avec succès`,
    }, 201);
  } catch (err: any) {
    console.error('[Upload] Error:', err);
    return c.json({ error: err.message || 'Erreur lors de l\'upload' }, 500);
  }
});

export { router as uploadRoutes };
