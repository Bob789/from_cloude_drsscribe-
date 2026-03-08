import 'package:flutter/material.dart';

enum StatCardLayout { verticalGlow, horizontalLuxury, verticalMinimal }

class MedScribeThemeExtension extends ThemeExtension<MedScribeThemeExtension> {
  final BoxDecoration cardDecoration;
  final BoxDecoration statCardDecoration;
  final BoxDecoration sidebarDecoration;
  final BoxDecoration selectedNavDecoration;
  final BoxDecoration avatarRingDecoration;
  final BoxDecoration chartBarDefault;
  final BoxDecoration chartBarHovered;

  final BoxDecoration Function(Color color) buildIconContainer;

  final StatCardLayout statCardLayout;
  final double statCardAspectRatio;
  final double cardRadius;
  final double navItemRadius;

  final Color selectedNavIconColor;
  final Color selectedNavTextColor;
  final Color success;
  final Color dividerColor;
  final List<Color> gradientColors;

  final Map<String, Color> urgencyColors;
  final Map<String, Color> statusColors;

  MedScribeThemeExtension({
    required this.cardDecoration,
    required this.statCardDecoration,
    required this.sidebarDecoration,
    required this.selectedNavDecoration,
    required this.avatarRingDecoration,
    required this.chartBarDefault,
    required this.chartBarHovered,
    required this.buildIconContainer,
    required this.statCardLayout,
    required this.statCardAspectRatio,
    required this.cardRadius,
    required this.navItemRadius,
    required this.selectedNavIconColor,
    required this.selectedNavTextColor,
    required this.success,
    required this.dividerColor,
    required this.gradientColors,
    required this.urgencyColors,
    required this.statusColors,
  });

  BoxDecoration chartBarDecoration(bool isHovered) =>
      isHovered ? chartBarHovered : chartBarDefault;

  BoxDecoration iconContainer(Color color) => buildIconContainer(color);

  @override
  ThemeExtension<MedScribeThemeExtension> copyWith() => this;

  @override
  ThemeExtension<MedScribeThemeExtension> lerp(
    covariant ThemeExtension<MedScribeThemeExtension>? other,
    double t,
  ) =>
      this;
}
