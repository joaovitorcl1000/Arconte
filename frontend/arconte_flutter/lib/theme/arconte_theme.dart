import 'package:flutter/material.dart';

/// Paleta original do Arconte: tinta, bosque, pergaminho e latão envelhecido.
abstract final class ArconteColors {
  static const ink = Color(0xFF172629);
  static const night = Color(0xFF112022);
  static const forest = Color(0xFF234940);
  static const forestLight = Color(0xFF356457);
  static const moss = Color(0xFF78917B);
  static const parchment = Color(0xFFF0E9DB);
  static const paper = Color(0xFFFBF7EE);
  static const softPaper = Color(0xFFF4EEDF);
  static const brass = Color(0xFFAF8753);
  static const paleGold = Color(0xFFE9D3A6);
  static const crimson = Color(0xFF8F4C46);
  static const text = Color(0xFF293632);
  static const secondaryText = Color(0xFF737971);
  static const border = Color(0xFFDCD2BE);
  static const white = Color(0xFFFFFCF6);
}

abstract final class ArconteTheme {
  static ThemeData get light {
    const scheme = ColorScheme.light(
      primary: ArconteColors.forest,
      onPrimary: ArconteColors.paper,
      secondary: ArconteColors.brass,
      onSecondary: ArconteColors.ink,
      surface: ArconteColors.paper,
      onSurface: ArconteColors.text,
      error: ArconteColors.crimson,
      onError: ArconteColors.paper,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: ArconteColors.parchment,
      splashColor: ArconteColors.brass.withValues(alpha: .10),
      highlightColor: Colors.transparent,
      dividerColor: ArconteColors.border,
      textTheme: const TextTheme(
        bodyMedium:
            TextStyle(fontSize: 14, color: ArconteColors.text, height: 1.45),
        bodyLarge:
            TextStyle(fontSize: 16, color: ArconteColors.text, height: 1.45),
        labelSmall: TextStyle(
            fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 1.8),
      ),
      inputDecorationTheme: InputDecorationTheme(
        isDense: true,
        filled: true,
        fillColor: ArconteColors.paper,
        hintStyle:
            const TextStyle(color: ArconteColors.secondaryText, fontSize: 13),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ArconteColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ArconteColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ArconteColors.brass, width: 1.5),
        ),
      ),
    );
  }
}

class ArconteType {
  static const display = TextStyle(
    fontFamily: 'serif',
    fontSize: 42,
    fontWeight: FontWeight.w600,
    height: 1.06,
    color: ArconteColors.ink,
    letterSpacing: -.8,
  );
  static const heading = TextStyle(
    fontFamily: 'serif',
    fontSize: 27,
    fontWeight: FontWeight.w600,
    height: 1.2,
    color: ArconteColors.ink,
  );
  static const cardTitle = TextStyle(
    fontFamily: 'serif',
    fontSize: 21,
    fontWeight: FontWeight.w600,
    height: 1.2,
    color: ArconteColors.ink,
  );
}
