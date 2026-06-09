import 'package:flutter/material.dart';

// Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
// Contract: design-system-v1.md SCREEN-001 mobile login shell; api-specs-v1.md API-001/API-002 mock OTP flow
class LoginOtpScreen extends StatefulWidget {
  const LoginOtpScreen({super.key});

  @override
  State<LoginOtpScreen> createState() => _LoginOtpScreenState();
}

class _LoginOtpScreenState extends State<LoginOtpScreen> {
  final TextEditingController identifier = TextEditingController();
  final TextEditingController otp = TextEditingController();
  bool challengeRequested = false;

  @override
  void dispose() {
    identifier.dispose();
    otp.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Semantics(
          identifier: challengeRequested ? 'login-form' : 'login-empty',
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 360),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('Đăng nhập để mua vé'),
                TextField(
                  controller: identifier,
                  decoration: const InputDecoration(labelText: 'Email hoặc số điện thoại'),
                  onChanged: (_) => setState(() {}),
                ),
                if (challengeRequested) ...[
                  TextField(controller: otp, decoration: const InputDecoration(labelText: 'Mã OTP')),
                  const Text('Demo OTP: 000000'),
                ],
                ElevatedButton(
                  onPressed: identifier.text.trim().isEmpty
                      ? null
                      : () => setState(() {
                            challengeRequested = true;
                          }),
                  child: const Text('Tiếp tục'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
