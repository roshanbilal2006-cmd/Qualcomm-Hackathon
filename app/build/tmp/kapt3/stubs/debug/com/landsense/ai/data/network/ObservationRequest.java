package com.landsense.ai.data.network;

@kotlinx.serialization.Serializable()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000B\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010 \n\u0002\u0010\u000e\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0002\b\u0012\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0010\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\b\u0087\b\u0018\u0000 -2\u00020\u0001:\u0002,-B[\b\u0011\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u000e\u0010\u0004\u001a\n\u0012\u0004\u0012\u00020\u0006\u0018\u00010\u0005\u0012\b\u0010\u0007\u001a\u0004\u0018\u00010\u0006\u0012\b\u0010\b\u001a\u0004\u0018\u00010\u0006\u0012\b\u0010\t\u001a\u0004\u0018\u00010\u0006\u0012\b\u0010\n\u001a\u0004\u0018\u00010\u0006\u0012\b\u0010\u000b\u001a\u0004\u0018\u00010\u0006\u0012\b\u0010\f\u001a\u0004\u0018\u00010\r\u00a2\u0006\u0002\u0010\u000eB?\u0012\f\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005\u0012\u0006\u0010\u0007\u001a\u00020\u0006\u0012\u0006\u0010\b\u001a\u00020\u0006\u0012\u0006\u0010\t\u001a\u00020\u0006\u0012\b\u0010\n\u001a\u0004\u0018\u00010\u0006\u0012\b\b\u0002\u0010\u000b\u001a\u00020\u0006\u00a2\u0006\u0002\u0010\u000fJ\u000f\u0010\u0018\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005H\u00c6\u0003J\t\u0010\u0019\u001a\u00020\u0006H\u00c6\u0003J\t\u0010\u001a\u001a\u00020\u0006H\u00c6\u0003J\t\u0010\u001b\u001a\u00020\u0006H\u00c6\u0003J\u000b\u0010\u001c\u001a\u0004\u0018\u00010\u0006H\u00c6\u0003J\t\u0010\u001d\u001a\u00020\u0006H\u00c6\u0003JM\u0010\u001e\u001a\u00020\u00002\u000e\b\u0002\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00060\u00052\b\b\u0002\u0010\u0007\u001a\u00020\u00062\b\b\u0002\u0010\b\u001a\u00020\u00062\b\b\u0002\u0010\t\u001a\u00020\u00062\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\u00062\b\b\u0002\u0010\u000b\u001a\u00020\u0006H\u00c6\u0001J\u0013\u0010\u001f\u001a\u00020 2\b\u0010!\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\"\u001a\u00020\u0003H\u00d6\u0001J\t\u0010#\u001a\u00020\u0006H\u00d6\u0001J&\u0010$\u001a\u00020%2\u0006\u0010&\u001a\u00020\u00002\u0006\u0010\'\u001a\u00020(2\u0006\u0010)\u001a\u00020*H\u00c1\u0001\u00a2\u0006\u0002\b+R\u0011\u0010\u000b\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0010\u0010\u0011R\u0017\u0010\u0004\u001a\b\u0012\u0004\u0012\u00020\u00060\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0013R\u0011\u0010\u0007\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u0011R\u0011\u0010\b\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0015\u0010\u0011R\u0011\u0010\t\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0016\u0010\u0011R\u0013\u0010\n\u001a\u0004\u0018\u00010\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0017\u0010\u0011\u00a8\u0006."}, d2 = {"Lcom/landsense/ai/data/network/ObservationRequest;", "", "seen1", "", "images", "", "", "latitude", "longitude", "timestamp", "voice_query", "device", "serializationConstructorMarker", "Lkotlinx/serialization/internal/SerializationConstructorMarker;", "(ILjava/util/List;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lkotlinx/serialization/internal/SerializationConstructorMarker;)V", "(Ljava/util/List;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V", "getDevice", "()Ljava/lang/String;", "getImages", "()Ljava/util/List;", "getLatitude", "getLongitude", "getTimestamp", "getVoice_query", "component1", "component2", "component3", "component4", "component5", "component6", "copy", "equals", "", "other", "hashCode", "toString", "write$Self", "", "self", "output", "Lkotlinx/serialization/encoding/CompositeEncoder;", "serialDesc", "Lkotlinx/serialization/descriptors/SerialDescriptor;", "write$Self$app_debug", "$serializer", "Companion", "app_debug"})
public final class ObservationRequest {
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<java.lang.String> images = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String latitude = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String longitude = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String timestamp = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String voice_query = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String device = null;
    @org.jetbrains.annotations.NotNull()
    public static final com.landsense.ai.data.network.ObservationRequest.Companion Companion = null;
    
    public ObservationRequest(@org.jetbrains.annotations.NotNull()
    java.util.List<java.lang.String> images, @org.jetbrains.annotations.NotNull()
    java.lang.String latitude, @org.jetbrains.annotations.NotNull()
    java.lang.String longitude, @org.jetbrains.annotations.NotNull()
    java.lang.String timestamp, @org.jetbrains.annotations.Nullable()
    java.lang.String voice_query, @org.jetbrains.annotations.NotNull()
    java.lang.String device) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<java.lang.String> getImages() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getLatitude() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getLongitude() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getTimestamp() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getVoice_query() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getDevice() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<java.lang.String> component1() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component2() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component3() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component4() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component5() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.landsense.ai.data.network.ObservationRequest copy(@org.jetbrains.annotations.NotNull()
    java.util.List<java.lang.String> images, @org.jetbrains.annotations.NotNull()
    java.lang.String latitude, @org.jetbrains.annotations.NotNull()
    java.lang.String longitude, @org.jetbrains.annotations.NotNull()
    java.lang.String timestamp, @org.jetbrains.annotations.Nullable()
    java.lang.String voice_query, @org.jetbrains.annotations.NotNull()
    java.lang.String device) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
    
    @kotlin.jvm.JvmStatic()
    public static final void write$Self$app_debug(@org.jetbrains.annotations.NotNull()
    com.landsense.ai.data.network.ObservationRequest self, @org.jetbrains.annotations.NotNull()
    kotlinx.serialization.encoding.CompositeEncoder output, @org.jetbrains.annotations.NotNull()
    kotlinx.serialization.descriptors.SerialDescriptor serialDesc) {
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00006\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0011\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\b\u00c7\u0002\u0018\u00002\b\u0012\u0004\u0012\u00020\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0003J\u0018\u0010\b\u001a\f\u0012\b\u0012\u0006\u0012\u0002\b\u00030\n0\tH\u00d6\u0001\u00a2\u0006\u0002\u0010\u000bJ\u0011\u0010\f\u001a\u00020\u00022\u0006\u0010\r\u001a\u00020\u000eH\u00d6\u0001J\u0019\u0010\u000f\u001a\u00020\u00102\u0006\u0010\u0011\u001a\u00020\u00122\u0006\u0010\u0013\u001a\u00020\u0002H\u00d6\u0001R\u0014\u0010\u0004\u001a\u00020\u00058VX\u00d6\u0005\u00a2\u0006\u0006\u001a\u0004\b\u0006\u0010\u0007\u00a8\u0006\u0014"}, d2 = {"com/landsense/ai/data/network/ObservationRequest.$serializer", "Lkotlinx/serialization/internal/GeneratedSerializer;", "Lcom/landsense/ai/data/network/ObservationRequest;", "()V", "descriptor", "Lkotlinx/serialization/descriptors/SerialDescriptor;", "getDescriptor", "()Lkotlinx/serialization/descriptors/SerialDescriptor;", "childSerializers", "", "Lkotlinx/serialization/KSerializer;", "()[Lkotlinx/serialization/KSerializer;", "deserialize", "decoder", "Lkotlinx/serialization/encoding/Decoder;", "serialize", "", "encoder", "Lkotlinx/serialization/encoding/Encoder;", "value", "app_debug"})
    @java.lang.Deprecated()
    public static final class $serializer implements kotlinx.serialization.internal.GeneratedSerializer<com.landsense.ai.data.network.ObservationRequest> {
        @org.jetbrains.annotations.NotNull()
        public static final com.landsense.ai.data.network.ObservationRequest.$serializer INSTANCE = null;
        
        private $serializer() {
            super();
        }
        
        @java.lang.Override()
        @org.jetbrains.annotations.NotNull()
        public kotlinx.serialization.KSerializer<?>[] childSerializers() {
            return null;
        }
        
        @java.lang.Override()
        @org.jetbrains.annotations.NotNull()
        public com.landsense.ai.data.network.ObservationRequest deserialize(@org.jetbrains.annotations.NotNull()
        kotlinx.serialization.encoding.Decoder decoder) {
            return null;
        }
        
        @java.lang.Override()
        @org.jetbrains.annotations.NotNull()
        public kotlinx.serialization.descriptors.SerialDescriptor getDescriptor() {
            return null;
        }
        
        @java.lang.Override()
        public void serialize(@org.jetbrains.annotations.NotNull()
        kotlinx.serialization.encoding.Encoder encoder, @org.jetbrains.annotations.NotNull()
        com.landsense.ai.data.network.ObservationRequest value) {
        }
        
        @java.lang.Override()
        @org.jetbrains.annotations.NotNull()
        public kotlinx.serialization.KSerializer<?>[] typeParametersSerializers() {
            return null;
        }
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0016\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u000f\u0010\u0003\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004H\u00c6\u0001\u00a8\u0006\u0006"}, d2 = {"Lcom/landsense/ai/data/network/ObservationRequest$Companion;", "", "()V", "serializer", "Lkotlinx/serialization/KSerializer;", "Lcom/landsense/ai/data/network/ObservationRequest;", "app_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
        
        @org.jetbrains.annotations.NotNull()
        public final kotlinx.serialization.KSerializer<com.landsense.ai.data.network.ObservationRequest> serializer() {
            return null;
        }
    }
}