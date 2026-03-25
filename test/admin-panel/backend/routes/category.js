const express = require('express');
const { body, validationResult } = require('express-validator');
const { PrismaClient } = require('@prisma/client');
const { authenticate } = require('../middleware/auth');
const { slugify } = require('../utils/slugify');

const router = express.Router();
const prisma = new PrismaClient();

router.get('/', async (req, res) => {
  try {
    const categories = await prisma.category.findMany({
      include: { _count: { select: { contents: true } } },
      orderBy: { name: 'asc' }
    });
    res.json(categories);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const category = await prisma.category.findUnique({
      where: { id: parseInt(req.params.id) },
      include: { contents: true }
    });

    if (!category) {
      return res.status(404).json({ error: 'Kategori bulunamadı' });
    }

    res.json(category);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', authenticate, [
  body('name').notEmpty().trim()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, description } = req.body;
    const slug = slugify(name);

    const category = await prisma.category.create({
      data: { name, slug, description }
    });

    res.status(201).json(category);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', authenticate, async (req, res) => {
  try {
    const data = req.body;
    if (data.name && !data.slug) {
      data.slug = slugify(data.name);
    }

    const category = await prisma.category.update({
      where: { id: parseInt(req.params.id) },
      data
    });

    res.json(category);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', authenticate, async (req, res) => {
  try {
    await prisma.category.delete({
      where: { id: parseInt(req.params.id) }
    });

    res.json({ message: 'Kategori silindi' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;