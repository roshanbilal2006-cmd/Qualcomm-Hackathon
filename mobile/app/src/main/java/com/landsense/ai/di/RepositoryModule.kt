package com.landsense.ai.di

import com.landsense.ai.data.repository.ObservationRepository
import com.landsense.ai.data.repository.ObservationRepositoryImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindObservationRepository(
        observationRepositoryImpl: ObservationRepositoryImpl
    ): ObservationRepository
}
