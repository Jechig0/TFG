import { fakeAsync, flushMicrotasks, TestBed } from '@angular/core/testing';
import { AlumnoPageComponent } from './alumno-page.component';
import { of, throwError } from 'rxjs';
import Swal from 'sweetalert2';
import { AlumnosService } from '@/alumnos/services/alumnos.service';
import { ActivatedRoute, Router } from '@angular/router';
import { AlumnoStateService } from '@/alumnos/services/alumno-state.service';

// ---- Mocks de servicios ----
const mockAlumnosService = {
  getAlumnoById: jasmine.createSpy('getAlumnoById').and.returnValue(of({ id: 1, nombre: 'Test' })),
  eliminarAlumno: jasmine.createSpy('eliminarAlumno').and.returnValue(of({}))
};

const mockAlumnoStateService = {
  clear: jasmine.createSpy('clear')
};

const mockActivatedRoute = {
  snapshot: {
    params: { id: 1 }
  }
};

const mockRouter = {
  navigate: jasmine.createSpy('navigate')
};

// ---- Mock global de SweetAlert ----
describe('AlumnoPageComponent', () => {

  beforeEach(() => {
    spyOn(Swal, 'fire').and.returnValue(Promise.resolve({ isConfirmed: true }) as any);

    TestBed.configureTestingModule({
      imports: [
        AlumnoPageComponent
      ],
      providers: [
        { provide: ActivatedRoute, useValue: mockActivatedRoute },
        { provide: Router, useValue: mockRouter },
        { provide: AlumnoStateService, useValue: mockAlumnoStateService },
        { provide: AlumnosService, useValue: mockAlumnosService },
      ]
    });
  });

  function createComponent() {
    const fixture = TestBed.createComponent(AlumnoPageComponent);
    const component = fixture.componentInstance;
    fixture.detectChanges();
    return { fixture, component };
  }

  // --------------------------------------------------------------------

  it('should create the component', () => {
    const { component } = createComponent();
    expect(component).toBeTruthy();
  });

  // --------------------------------------------------------------------
  // actualizarExpediente()
  // --------------------------------------------------------------------

  it('should navigate when calling actualizarExpediente', () => {
    const { component } = createComponent();

    component.actualizarExpediente();

    expect(mockRouter.navigate).toHaveBeenCalledWith(['/nuevo-alumno/1']);
  });

  // --------------------------------------------------------------------
  // borrarExpediente() - confirmación OK
  // --------------------------------------------------------------------

it('should delete expediente when Swal confirms', fakeAsync(() => {
    // Swal.fire devuelve una Promise que se resolverá con { isConfirmed: true }
    (Swal.fire as jasmine.Spy).and.returnValue(Promise.resolve({ isConfirmed: true }) as any);
    mockAlumnosService.eliminarAlumno.and.returnValue(of({})); // observable síncrono

    const { component } = createComponent();

    component.borrarExpediente();

    // Ejecuta microtasks para resolver la Promise de Swal.fire y ejecutar la suscripción
    flushMicrotasks();

    expect(Swal.fire).toHaveBeenCalled();
    expect(mockAlumnosService.eliminarAlumno).toHaveBeenCalledWith(1);
    expect(mockAlumnoStateService.clear).toHaveBeenCalled();
    expect(mockRouter.navigate).toHaveBeenCalledWith(['/']);
  }));

  // --------------------------------------------------------------------
  // borrarExpediente() - error al borrar
  // --------------------------------------------------------------------

  it('should show error when eliminarAlumno fails', fakeAsync(() => {
    (Swal.fire as jasmine.Spy).and.returnValue(Promise.resolve({ isConfirmed: true }) as any);
    mockAlumnosService.eliminarAlumno.and.returnValue(throwError(() => ({ error: { detail: 'Error test' } })));

    const { component } = createComponent();

    component.borrarExpediente();
    flushMicrotasks();

    expect(Swal.fire).toHaveBeenCalled();
    expect(mockAlumnosService.eliminarAlumno).toHaveBeenCalledWith(1);
    // Opcional: comprobar que se llamó a Swal.fire para el error (segundo Swal)
    expect((Swal.fire as jasmine.Spy).calls.count()).toBeGreaterThanOrEqual(2);
  }));

  it('should show default error message when deletion fails without detail', async () => {
    const { component } = createComponent();

    // Simula que Swal confirma la acción
    (Swal.fire as jasmine.Spy).and.returnValue(Promise.resolve({ isConfirmed: true }));

    // Simula que el service falla SIN err.error.detail
    mockAlumnosService.eliminarAlumno.and.returnValue(throwError(() => ({
      error: {}
    })));

    await component.borrarExpediente();

    expect(Swal.fire).toHaveBeenCalledWith(
      'Error',
      'No se pudo borrar el expediente.',
      'error'
    );
  });


  // --------------------------------------------------------------------
  // logout()
  // --------------------------------------------------------------------

  it('should clear session and navigate on logout confirmation', async () => {
    spyOn(sessionStorage, 'clear');

    const { component } = createComponent();

    await component.logout();

    expect(sessionStorage.clear).toHaveBeenCalled();
    expect(mockRouter.navigate).toHaveBeenCalledWith(['/']);
  });

  // --------------------------------------------------------------------
  // Carga de datos vía rxResource
  // --------------------------------------------------------------------


});
