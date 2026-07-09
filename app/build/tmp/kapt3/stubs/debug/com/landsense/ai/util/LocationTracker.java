package com.landsense.ai.util;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0012\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\bf\u0018\u00002\u00020\u0001J\u0010\u0010\u0002\u001a\u0004\u0018\u00010\u0003H\u00a6@\u00a2\u0006\u0002\u0010\u0004\u00a8\u0006\u0005"}, d2 = {"Lcom/landsense/ai/util/LocationTracker;", "", "getCurrentLocation", "Landroid/location/Location;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public abstract interface LocationTracker {
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getCurrentLocation(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super android.location.Location> $completion);
}