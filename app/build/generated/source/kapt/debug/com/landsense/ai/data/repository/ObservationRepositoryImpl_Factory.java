package com.landsense.ai.data.repository;

import com.landsense.ai.data.network.ApiService;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava",
    "cast"
})
public final class ObservationRepositoryImpl_Factory implements Factory<ObservationRepositoryImpl> {
  private final Provider<ApiService> apiServiceProvider;

  public ObservationRepositoryImpl_Factory(Provider<ApiService> apiServiceProvider) {
    this.apiServiceProvider = apiServiceProvider;
  }

  @Override
  public ObservationRepositoryImpl get() {
    return newInstance(apiServiceProvider.get());
  }

  public static ObservationRepositoryImpl_Factory create(Provider<ApiService> apiServiceProvider) {
    return new ObservationRepositoryImpl_Factory(apiServiceProvider);
  }

  public static ObservationRepositoryImpl newInstance(ApiService apiService) {
    return new ObservationRepositoryImpl(apiService);
  }
}
