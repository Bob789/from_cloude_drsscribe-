import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/timer_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;

class TreatmentTimer extends ConsumerStatefulWidget {
  final bool compact;
  const TreatmentTimer({super.key, this.compact = false});

  @override
  ConsumerState<TreatmentTimer> createState() => _TreatmentTimerState();
}

class _TreatmentTimerState extends ConsumerState<TreatmentTimer> with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  static const _durations = [10, 15, 20, 25, 30, 45, 60];

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(vsync: this, duration: const Duration(seconds: 1));
    _animController.repeat();
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  Color _progressColor(double progress) {
    if (progress >= 0.9) return const Color(0xFFEF4444);
    if (progress >= 0.8) return const Color(0xFFF59E0B);
    return const Color(0xFF22C55E);
  }

  Color _glowColor(double progress) {
    if (progress >= 0.9) return const Color(0xFFFF6B6B);
    if (progress >= 0.8) return const Color(0xFFFFD93D);
    return const Color(0xFF4ADE80);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(timerProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final circleSize = widget.compact ? 120.0 : 160.0;

    return Container(
      padding: EdgeInsets.all(widget.compact ? 16 : 24),
      decoration: ext.cardDecoration,
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        if (!widget.compact)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              Icon(Icons.timer_rounded, size: 20, color: AppColors.primary),
              const SizedBox(width: 8),
              Text('timer.title'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
            ]),
          ),
        AnimatedBuilder(
          animation: _animController,
          builder: (context, _) {
            return SizedBox(
              width: circleSize,
              height: circleSize,
              child: CustomPaint(
                painter: _TimerPainter(
                  progress: state.progress,
                  fillColor: _progressColor(state.progress),
                  glowColor: _glowColor(state.progress),
                  bgColor: AppColors.cardBorder,
                  isDone: state.isDone,
                ),
                child: Center(
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    Text(
                      state.isIdle ? '${state.totalSeconds ~/ 60}:00' : state.remainingFormatted,
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: widget.compact ? 22 : 28,
                        fontWeight: FontWeight.w700,
                        color: state.isDone ? const Color(0xFFEF4444) : AppColors.textPrimary,
                      ),
                    ),
                    if (!state.isIdle && !widget.compact)
                      Text(
                        state.isDone ? 'timer.done'.tr() : 'timer.remaining'.tr(),
                        style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted),
                      ),
                  ]),
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 16),
        if (state.isIdle) ...[
          SizedBox(
            height: 36,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              shrinkWrap: true,
              separatorBuilder: (_, __) => const SizedBox(width: 6),
              itemCount: _durations.length,
              itemBuilder: (_, i) {
                final d = _durations[i];
                final selected = state.totalSeconds == d * 60;
                return GestureDetector(
                  onTap: () => ref.read(timerProvider.notifier).setDuration(d),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: selected ? AppColors.primary.withValues(alpha: 0.15) : Colors.transparent,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: selected ? AppColors.primary : AppColors.cardBorder),
                    ),
                    child: Text('$d\'', style: GoogleFonts.heebo(
                      fontSize: 13, fontWeight: selected ? FontWeight.w700 : FontWeight.w400,
                      color: selected ? AppColors.primary : AppColors.textSecondary,
                    )),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 14),
          _ActionButton(label: 'timer.start'.tr(), icon: Icons.play_arrow_rounded, onTap: () => ref.read(timerProvider.notifier).start()),
        ] else if (state.isRunning) ...[
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            _ActionButton(label: 'timer.pause'.tr(), icon: Icons.pause_rounded, onTap: () => ref.read(timerProvider.notifier).pause(), small: true),
            const SizedBox(width: 10),
            _ActionButton(label: 'timer.reset'.tr(), icon: Icons.stop_rounded, onTap: () => ref.read(timerProvider.notifier).reset(), small: true, secondary: true),
          ]),
        ] else if (state.isPaused) ...[
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            _ActionButton(label: 'timer.resume'.tr(), icon: Icons.play_arrow_rounded, onTap: () => ref.read(timerProvider.notifier).resume(), small: true),
            const SizedBox(width: 10),
            _ActionButton(label: 'timer.reset'.tr(), icon: Icons.stop_rounded, onTap: () => ref.read(timerProvider.notifier).reset(), small: true, secondary: true),
          ]),
        ] else if (state.isDone) ...[
          Text('timer.finished'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w700, color: const Color(0xFFEF4444))),
          const SizedBox(height: 10),
          _ActionButton(label: 'timer.new_treatment'.tr(), icon: Icons.refresh_rounded, onTap: () => ref.read(timerProvider.notifier).reset()),
        ],
      ]),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final bool small;
  final bool secondary;

  const _ActionButton({required this.label, required this.icon, required this.onTap, this.small = false, this.secondary = false});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: EdgeInsets.symmetric(horizontal: small ? 16 : 24, vertical: small ? 10 : 12),
          decoration: BoxDecoration(
            gradient: secondary ? null : LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
            color: secondary ? AppColors.background : null,
            borderRadius: BorderRadius.circular(10),
            border: secondary ? Border.all(color: AppColors.cardBorder) : null,
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(icon, size: small ? 16 : 18, color: secondary ? AppColors.textSecondary : Colors.white),
            const SizedBox(width: 6),
            Text(label, style: GoogleFonts.heebo(
              fontSize: small ? 12 : 14, fontWeight: FontWeight.w600,
              color: secondary ? AppColors.textSecondary : Colors.white,
            )),
          ]),
        ),
      ),
    );
  }
}

class _TimerPainter extends CustomPainter {
  final double progress;
  final Color fillColor;
  final Color glowColor;
  final Color bgColor;
  final bool isDone;

  _TimerPainter({
    required this.progress,
    required this.fillColor,
    required this.glowColor,
    required this.bgColor,
    this.isDone = false,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 12;
    const strokeWidth = 10.0;

    final bgPaint = Paint()
      ..color = bgColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth - 2;
    canvas.drawCircle(center, radius, bgPaint);

    if (progress <= 0) return;

    final sweepAngle = 2 * pi * progress.clamp(0.0, 1.0);

    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -pi / 2,
      sweepAngle,
      false,
      fillPaint,
    );

    if (progress > 0.01 && progress < 1.0) {
      final tipAngle = -pi / 2 + sweepAngle;
      final tipX = center.dx + radius * cos(tipAngle);
      final tipY = center.dy + radius * sin(tipAngle);
      final glowPaint = Paint()
        ..color = glowColor.withValues(alpha: 0.4)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
      canvas.drawCircle(Offset(tipX, tipY), 6, glowPaint);
    }

    if (isDone) {
      final donePaint = Paint()
        ..color = fillColor.withValues(alpha: 0.08)
        ..style = PaintingStyle.fill;
      canvas.drawCircle(center, radius - strokeWidth / 2, donePaint);
    }
  }

  @override
  bool shouldRepaint(_TimerPainter old) =>
      old.progress != progress || old.fillColor != fillColor || old.isDone != isDone;
}
