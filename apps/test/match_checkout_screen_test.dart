import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ticket_mafia_app/features/matches/match_checkout_screen.dart';

void main() {
  testWidgets('match checkout shell enforces five seat limit and reaches pending state', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: MatchCheckoutScreen()));

    await tester.tap(find.text('Chọn ghế'));
    await tester.pump();

    for (var index = 1; index <= 5; index += 1) {
      await tester.tap(find.textContaining('A-T1-00$index'));
      await tester.pump();
    }
    await tester.tap(find.textContaining('A-T1-006'));
    await tester.pump();

    expect(find.text('5/5 ghế đã chọn'), findsOneWidget);
    expect(find.text('Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.'), findsOneWidget);

    await tester.tap(find.text('Thanh toán'));
    await tester.pump();
    expect(find.text('asset://payment/default'), findsOneWidget);

    await tester.tap(find.text('Tôi đã chuyển khoản'));
    await tester.pump();
    expect(find.text('Đang chờ admin xác nhận'), findsOneWidget);
  });
}
