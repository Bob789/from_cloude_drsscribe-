import 'package:flutter/material.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

class LoadingIndicator extends StatelessWidget {
  final double size;
  final double strokeWidth;

  const LoadingIndicator({super.key, this.size = 36, this.strokeWidth = 2.5});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: strokeWidth),
    );
  }
}
