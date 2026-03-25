const express = require('express');
const { body, validationResult } = require('express-validator');
const { PrismaClient } = require('@prisma/client');
const { authenticate } = require('../middleware/auth');

const router = express.Router();
const prisma = new PrismaClient();

router.get('/submissions', authenticate, async (req, res) => {
  try {
    const { status, formType, page = 1, limit = 10 } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {};
    if (status) where.status = status;
    if (formType) where.formType = formType;

    const [submissions, total] = await Promise.all([
      prisma.formSubmission.findMany({
        where,
        orderBy: { createdAt: 'desc' },
        skip,
        take: parseInt(limit)
      }),
      prisma.formSubmission.count({ where })
    ]);

    res.json({
      data: submissions,
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

router.get('/submissions/:id', authenticate, async (req, res) => {
  try {
    const submission = await prisma.formSubmission.findUnique({
      where: { id: parseInt(req.params.id) }
    });

    if (!submission) {
      return res.status(404).json({ error: 'Form gönderimi bulunamadı' });
    }

    res.json(submission);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/submit', [
  body('formType').notEmpty(),
  body('data').isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { formType, data } = req.body;

    const submission = await prisma.formSubmission.create({
      data: {
        formType,
        data,
        status: 'NEW'
      }
    });

    res.status(201).json({
      message: 'Form başarıyla gönderildi',
      submission
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/submissions/:id/status', authenticate, async (req, res) => {
  try {
    const { status, notes } = req.body;

    const submission = await prisma.formSubmission.update({
      where: { id: parseInt(req.params.id) },
      data: {
        status,
        notes,
        processedBy: req.user.id,
        processedAt: new Date()
      }
    });

    res.json(submission);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/submissions/:id', authenticate, async (req, res) => {
  try {
    await prisma.formSubmission.delete({
      where: { id: parseInt(req.params.id) }
    });

    res.json({ message: 'Form gönderimi silindi' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;