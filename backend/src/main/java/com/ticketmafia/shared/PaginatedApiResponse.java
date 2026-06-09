package com.ticketmafia.shared;

public record PaginatedApiResponse<T, M>(T data, M meta) {
}
