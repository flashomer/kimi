const express = require('express');
const { body, validationResult } = require('express-validator');
const { PrismaClient } = require('@prisma/client');
const { authenticate } = require('../middleware/auth');
const { slugify } = require('../utils/slugify');

const router = express.Router();
const prisma = new PrismaClient();

router.get('/', authenticate, async (req, res) => {
  try {
    const { type, status, search, page = 1, limit = 10 } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {};
    if (type) where.type = type;
    if (status) where.status = status;
    if (search) {
      where.OR = [
        { title: { contains: search, mode: 'insensitive' } },
        { content: { contains: search, mode: 'insensitive' } }
      ];
    }

    const [contents, total] = await Promise.all([
      prisma.content.findMany({
        where,
        include: { category: true },
        orderBy: { createdAt: 'desc' },
        skip,
        take: parseInt(limit)
      }),
      prisma.content.count({ where })
    ]);

    res.json({
      data: contents,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        totalPages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', authenticate, async (req, res) => {
  try {
    const content = await prisma.content.findUnique({
      where: { id: parseInt(req.params.id) },
      include: { category: true }
    });

    if (!content) {
      return res.status(404).json({ error: 'İçerik bulunamadı' });
    }

    res.json(content);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', authenticate, [
  body('title').notEmpty().trim(),
  body('content').notEmpty(),
  body('type').isIn(['PAGE', 'POST', 'SERVICE', 'PRODUCT'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const data = req.body;
    data.slug = data.slug || slugify(data.title);
    data.authorId = req.user.id;

    const content = await prisma.content.create({
      data,
      include: { category: true }
    });

    res.status(201).json(content);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', authenticate, async (req, res) => {
  try {
    const data = req.body;
    if (data.title && !data.slug) {
      data.slug = slugify(data.title);
    }

    const content = await prisma.content.update({
      where: { id: parseInt(req.params.id) },
      data,
      include: { category: true }
    });

    res.json(content);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', authenticate, async (req, res) => {
  try {
    await prisma.content.delete({
      where: { id: parseInt(req.params.id) }
    });

    res.json({ message: 'İçerik silindi' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;