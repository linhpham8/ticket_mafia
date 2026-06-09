import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ticket_mafia_app/features/auth/login_otp_screen.dart';

void main() {
  testWidgets('login shell enables challenge request after identifier entry', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginOtpScreen()));

    final continueButton = find.widgetWithText(ElevatedButton, 'Tiếp tục');
    expect(continueButton, findsOneWidget);
    expect(tester.widget<ElevatedButton>(continueButton).onPressed, isNull);

    await tester.enterText(find.byType(TextField).first, 'fan1@example.test');
    await tester.pump();

    expect(tester.widget<ElevatedButton>(continueButton).onPressed, isNotNull);
    await tester.tap(continueButton);
    await tester.pump();

    expect(find.text('Demo OTP: 000000'), findsOneWidget);
    expect(find.widgetWithText(TextField, 'Mã OTP'), findsOneWidget);
  });
}
