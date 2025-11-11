export type AsignaturaCountRaw = [string, number];

export interface AsignaturaCount {
  nombre: string;
  count: number;
}

export interface Ponderacion {
  year: string;    // formato "2019-20"
  peso: number;    // número entre 0 y 1
}
