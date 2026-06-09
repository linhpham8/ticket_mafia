import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ticket_mafia_app/features/exchange/seat_exchange_screen.dart';

void main() {
  testWidgets('seat exchange blocks cheaper and unavailable seats then continues eligible seat', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: SeatExchangeScreen()));

    expect(find.text('Đổi ghế'), findsOneWidget);
    expect(tester.widget<OutlinedButton>(find.byKey(const Key('exchange-seat-seat-cheaper'))).enabled, isFalse);
    expect(tester.widget<OutlinedButton>(find.byKey(const Key('exchange-seat-seat-held'))).enabled, isFalse);

    await tester.tap(find.byKey(const Key('exchange-seat-seat-higher')));
    await tester.pump();
    await tester.tap(find.text('Tiếp tục đổi ghế'));
    await tester.pump();

    expect(find.text('Đơn đổi ghế đã được tạo.'), findsOneWidget);
  });
}
