import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { Component, effect , computed, inject, signal } from '@angular/core';
import { FormBuilder, FormsModule, Validators } from '@angular/forms';
import {rxResource} from '@angular/core/rxjs-interop';
import { FilterByTextPipe } from '@/alumnos/pipes/filter-by-text.pipe';
import { ActivatedRoute } from '@angular/router';
import { PercentPipe } from '@angular/common';
import { firstValueFrom } from 'rxjs';

interface PredictionData {
  probabilidad: number | null;
  afinidad: number | null;
  loading: boolean;
}

@Component({
  selector: 'lista-asignaturas',
  imports: [FormsModule, FilterByTextPipe, PercentPipe],
  templateUrl: './lista-asignaturas.component.html',
})
export class ListaAsignaturasComponent {
  private fb = inject(FormBuilder);
  private alumnosService = inject(AlumnosService);
  private activatedRoute = inject(ActivatedRoute);

  private alumnoId = this.activatedRoute.snapshot.params['id'];

  searchText = signal<string>('');
  selectedAsignaturas = signal<string[]>([]);
  predictions = signal<Map<string, PredictionData>>(new Map());

  asignaturaResource = rxResource({
    loader: () => this.alumnosService.getAsignaturas(this.alumnoId)
  });

  //Añade la asignatura seleccionada a la lista de chuips y carga las predicciones.
  async onAsignaturaClick(asignatura: string) {
    if (!this.selectedAsignaturas().includes(asignatura)) {
      this.selectedAsignaturas.update(prev => [...prev, asignatura]);
      this.searchText.set('');
      await this.loadPredictions(asignatura);
    }
  }

  // Elimina una asignatura de la lista de chips y de las predicciones.
  removeAsignatura(asignatura: string) {
    this.selectedAsignaturas.update(prev =>
      prev.filter(subject => subject !== asignatura)
    );
    this.predictions.update(prev => {
      const newMap = new Map(prev);
      newMap.delete(asignatura);
      return newMap;
    });
  }

  // Carga las predicciones para una asignatura específica llamando al servicio para traerlas del backend.
  private async loadPredictions(asignatura: string) {
    this.predictions.update(prev => {
      const newMap = new Map(prev);
      newMap.set(asignatura, { probabilidad: null, afinidad: null, loading: true });
      return newMap;
    });

    try {
      const [probabilidad, afinidad] = await Promise.all([
        firstValueFrom(this.alumnosService.getProbabilidadAcceso(this.alumnoId, asignatura)),
        firstValueFrom(this.alumnosService.getAfinidadAsignatura(this.alumnoId, asignatura))
      ]);

      this.predictions.update(prev => {
        const newMap = new Map(prev);
        newMap.set(asignatura, { probabilidad, afinidad, loading: false });
        return newMap;
      });
    } catch (error) {
      console.error('Error loading predictions:', error);
      this.predictions.update(prev => {
        const newMap = new Map(prev);
        newMap.set(asignatura, { probabilidad: null, afinidad: null, loading: false });
        return newMap;
      });
    }
  }

  // Verifica si las predicciones para una asignatura están en proceso de carga.
  isLoadingPredictions(asignatura: string): boolean {
    return this.predictions()?.get(asignatura)?.loading ?? false;
  }

  // Obtiene la probabilidad de entrada para una asignatura específica.
  getProbabilidad(asignatura: string): number {
    return this.predictions()?.get(asignatura)?.probabilidad ?? 0;
  }

  // Obtiene la afinidad para una asignatura específica.
  getAfinidad(asignatura: string): number {
    return this.predictions()?.get(asignatura)?.afinidad ?? 0;
  }
}
