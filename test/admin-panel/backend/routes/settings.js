const express = require('express');
const { body, validationResult } = require('express-validator');
const { PrismaClient } = require('@prisma/client');
const { authenticate, requireAdmin } = require('../middleware/auth');

const router = express.Router();
const prisma = new PrismaClient();

router.get('/', async (req, res) => {
  try {
    const settings = await prisma.setting.findMany();
    const settingsObject = settings.reduce((acc, setting) => {
      acc[setting.key] = setting.value;
      return acc;
    }, {});

    res.json(settingsObject);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/public', async (req, res) => {
  try {
    const settings = await prisma.setting.findMany({
      where: { isPublic: true }
    });
    const settingsObject = settings.reduce((acc, setting) => {
      acc[setting.key] = setting.value;
      return acc;
    }, {});

    res.json(settingsObject);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/', authenticate, requireAdmin, async (req, res) => {
  try {
    const updates = req.body;
    const results = [];

    for (const [key, value] of Object.entries(updates)) {
      const setting = await prisma.setting.upsert({
        where: { key },
        update: { value: String(value) },
        create: { key, value: String(value) }
      });
      results.push(setting);
    }

    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', authenticate, requireAdmin, [
  body('key').notEmpty().trim(),
  body('value').notEmpty()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { key, value, isPublic = false } = req.body;

    const setting = await prisma.setting.create({
      data: { key, value, isPublic }
    });

    res.status(201).json(setting);
  } catch (error) {
    if (error.code === 'P2002') {
      return res.status(400).json({ error: 'Bu ayar anahtarı zaten var' });
    }
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:key', authenticate, requireAdmin, async (req, res) => {
  try {
    await prisma.setting.delete({
      where: { key: req.params.key }
    });

    res.json({ message: 'Ayar silindi' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;