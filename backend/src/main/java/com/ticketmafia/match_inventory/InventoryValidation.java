package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.math.BigDecimal;
import java.util.Set;
import org.springframework.http.HttpStatus;

final class InventoryValidation {
    private static final Set<String> SECTIONS = Set.of("A", "B", "C", "D");
    private static final int MAX_SEATS_PER_GENERATION = 1_000;

    private InventoryValidation() {
    }

    static InventorySlice slice(String sectionCode, Integer floorNo, Boolean isVip, ErrorCode code) {
        String normalizedSection = sectionCode == null ? "" : sectionCode.trim().toUpperCase();
        if (!SECTIONS.contains(normalizedSection)) {
            throw invalid(code, "sectionCode");
        }
        if (floorNo == null || (floorNo != 1 && floorNo != 2)) {
            throw invalid(code, "floorNo");
        }
        boolean vip = Boolean.TRUE.equals(isVip);
        if (vip && !"A".equals(normalizedSection)) {
            throw invalid(code, "isVip");
        }
        return new InventorySlice(normalizedSection, floorNo, vip);
    }

    static int seatCount(Integer seatCount) {
        if (seatCount == null || seatCount <= 0 || seatCount > MAX_SEATS_PER_GENERATION) {
            throw invalid(ErrorCode.SEAT_GENERATE_INVALID_REQUEST, "seatCount");
        }
        return seatCount;
    }

    static BigDecimal price(BigDecimal priceVnd) {
        if (priceVnd == null || priceVnd.signum() <= 0) {
            throw invalid(ErrorCode.PRICE_INVALID_REQUEST, "priceVnd");
        }
        return priceVnd;
    }

    static ApiException invalid(ErrorCode code, String details) {
        return new ApiException(HttpStatus.BAD_REQUEST, code, "Request violates the admin inventory contract.", details);
    }
}
