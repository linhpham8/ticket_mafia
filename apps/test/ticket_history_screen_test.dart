import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ticket_mafia_app/features/tickets/ticket_history_screen.dart';

void main() {
  testWidgets('ticket history opens issued QR detail and suppresses invalid QR', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: TicketHistoryScreen()));

    expect(find.text('Hanoi FC vs Saigon FC'), findsOneWidget);
    await tester.tap(find.text('A-T1-001 · ISSUED'));
    await tester.pump();

    expect(find.byKey(const Key('ticket-qr-card')), findsOneWidget);
    expect(find.text('tk_v1_signedopaque'), findsOneWidget);

    await tester.tap(find.text('Lịch sử mua vé'));
    await tester.pump();
    await tester.tap(find.text('A-T1-002 · CANCELLED'));
    await tester.pump();

    expect(find.byKey(const Key('ticket-qr-card')), findsNothing);
    expect(find.text('Vé này không còn hợp lệ để vào sân.'), findsOneWidget);
  });
}
