const express = require('express');
const { body, validationResult } = require('express-validator');
const { PrismaClient } = require('@prisma/client');
const { authenticate } = require('../middleware/auth');

const router = express.Router();
const prisma = new PrismaClient();

const buildMenuTree = (items, parentId = null) => {
  return items
    .filter(item => item.parentId === parentId)
    .sort((a, b) => a.order - b.order)
    .map(item => ({
      ...item,
      children: buildMenuTree(items, item.id)
    }));
};

router.get('/', async (req, res) => {
  try {
    const { location } = req.query;
    const where = { isActive: true };
    if (location) where.location = location;

    const items = await prisma.menuItem.findMany({
      where,
      orderBy: { order: 'asc' }
    });

    const tree = buildMenuTree(items);
    res.json(tree);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/all', authenticate, async (req, res) => {
  try {
    const items = await prisma.menuItem.findMany({
      orderBy: { order: 'asc' }
    });
    res.json(items);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', authenticate, async (req, res) => {
  try {
    const item = await prisma.menuItem.findUnique({
      where: { id: parseInt(req.params.id) }
    });

    if (!item) {
      return res.status(404).json({ error: 'Menü öğesi bulunamadı' });
    }

    res.json(item);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', authenticate, [
  body('title').notEmpty().trim(),
  body('url').notEmpty().trim()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const data = req.body;
    
    const maxOrder = await prisma.menuItem.findFirst({
      where: { parentId: data.parentId || null },
      orderBy: { order: 'desc' }
    });
    
    data.order = data.order || (maxOrder ? maxOrder.order + 1 : 0);

    const item = await prisma.menuItem.create({ data });
    res.status(201).json(item);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', authenticate, async (req, res) => {
  try {
    const item = await prisma.menuItem.update({
      where: { id: parseInt(req.params.id) },
      data: req.body
    });

    res.json(item);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/reorder', authenticate, async (req, res) => {
  try {
    const { items } = req.body;

    await prisma.$transaction(
      items.map((item, index) =>
        prisma.menuItem.update({
          where: { id: item.id },
          data: { order: index, parentId: item.parentId }
        })
      )
    );

    res.json({ message: 'Menü sıralandı' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', authenticate, async (req, res) => {
  try {
    await prisma.menuItem.delete({
      where: { id: parseInt(req.params.id) }
    });

    res.json({ message: 'Menü öğesi silindi' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;