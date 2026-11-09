import 'package:flutter/material.dart';

/// Catálogo visual, sem serviços nem conexão com os módulos Python ainda.
class WorldModule {
  const WorldModule({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.category,
    required this.backendImplemented,
    this.example,
  });

  final String id;
  final String name;
  final String description;
  final IconData icon;
  final String category;
  final bool backendImplemented;
  final String? example;
}
