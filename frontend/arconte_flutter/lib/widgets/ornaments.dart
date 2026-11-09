import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/arconte_theme.dart';

/// Ilustração vetorial produzida com Flutter CustomPainter: nenhuma imagem externa.
class CitadelPainter extends CustomPainter {
  const CitadelPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final stars = Paint()..color = ArconteColors.paleGold.withValues(alpha: .5);
    for (var i = 0; i < 35; i++) {
      final x = w * ((i * 31 % 101) / 101);
      final y = h * ((i * 47 % 93) / 110);
      canvas.drawCircle(Offset(x, y), i % 6 == 0 ? 1.9 : 1.0, stars);
    }

    final ringPaint = Paint()
      ..color = ArconteColors.paleGold.withValues(alpha: .22)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    final center = Offset(w * .70, h * .52);
    canvas.drawCircle(center, h * .52, ringPaint);
    canvas.drawCircle(center, h * .42, ringPaint);
    canvas.drawCircle(center, h * .28, ringPaint);
    for (var i = 0; i < 12; i++) {
      final angle = math.pi * 2 * i / 12;
      final x1 = center.dx + math.cos(angle) * h * .44;
      final y1 = center.dy + math.sin(angle) * h * .44;
      final x2 = center.dx + math.cos(angle) * h * .50;
      final y2 = center.dy + math.sin(angle) * h * .50;
      canvas.drawLine(Offset(x1, y1), Offset(x2, y2), ringPaint);
    }

    final backMountain = Path()
      ..moveTo(w * .30, h)
      ..lineTo(w * .53, h * .35)
      ..lineTo(w * .63, h * .69)
      ..lineTo(w * .75, h * .29)
      ..lineTo(w, h * .92)
      ..lineTo(w, h)
      ..close();
    canvas.drawPath(backMountain,
        Paint()..color = const Color(0xFF568578).withValues(alpha: .24));

    final frontMountain = Path()
      ..moveTo(w * .37, h)
      ..lineTo(w * .63, h * .63)
      ..lineTo(w * .72, h * .85)
      ..lineTo(w * .87, h * .56)
      ..lineTo(w, h * .79)
      ..lineTo(w, h)
      ..close();
    canvas.drawPath(frontMountain,
        Paint()..color = const Color(0xFF0C2729).withValues(alpha: .82));

    // Silhueta de uma cidadela ao longe.
    final tower = Paint()..color = const Color(0xFF0A2022);
    final baseY = h * .75;
    canvas.drawRect(
        Rect.fromLTWH(w * .72, baseY - h * .10, w * .14, h * .22), tower);
    canvas.drawRect(
        Rect.fromLTWH(w * .745, baseY - h * .23, w * .035, h * .29), tower);
    canvas.drawRect(
        Rect.fromLTWH(w * .818, baseY - h * .20, w * .03, h * .25), tower);
    final roofs = Path()
      ..moveTo(w * .735, baseY - h * .23)
      ..lineTo(w * .763, baseY - h * .34)
      ..lineTo(w * .788, baseY - h * .23)
      ..moveTo(w * .808, baseY - h * .20)
      ..lineTo(w * .833, baseY - h * .30)
      ..lineTo(w * .86, baseY - h * .20);
    canvas.drawPath(
        roofs,
        Paint()
          ..color = const Color(0xFF0A2022)
          ..strokeWidth = 7
          ..strokeCap = StrokeCap.square
          ..style = PaintingStyle.stroke);
    final windows = Paint()
      ..color = ArconteColors.paleGold.withValues(alpha: .8);
    canvas.drawRect(Rect.fromLTWH(w * .759, baseY - h * .16, 3, 7), windows);
    canvas.drawRect(Rect.fromLTWH(w * .832, baseY - h * .12, 3, 6), windows);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class DecorativeRule extends StatelessWidget {
  const DecorativeRule({super.key, this.width = 108});

  final double width;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: width, height: 1, color: ArconteColors.brass),
        const SizedBox(width: 7),
        Transform.rotate(
          angle: math.pi / 4,
          child: Container(width: 5, height: 5, color: ArconteColors.brass),
        ),
      ],
    );
  }
}

class SmallCaps extends StatelessWidget {
  const SmallCaps(this.text, {super.key, this.color = ArconteColors.brass});

  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      style: TextStyle(
        fontSize: 10,
        fontWeight: FontWeight.w800,
        letterSpacing: 2,
        color: color,
      ),
    );
  }
}
