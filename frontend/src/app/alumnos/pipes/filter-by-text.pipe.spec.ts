import { FilterByTextPipe } from "./filter-by-text.pipe";

const mockAsignaturas = [
  'Matemáticas',
  'Historia',
];

describe('FilterByTextPipe', () => {
  let pipe: FilterByTextPipe;

  beforeEach(() => {
    pipe = new FilterByTextPipe();
  })

  it('should return all subjects if search text is empty', () => {
    const result = pipe.transform(mockAsignaturas, '');
    expect(result.length).toBe(2);
    expect(result).toEqual(mockAsignaturas);
  });

  it('should filter subjects by search text', () => {
    const result = pipe.transform(mockAsignaturas, 'mat');
    expect(result.length).toBe(1);
    expect(result).toEqual(['Matemáticas']);
  });

});
