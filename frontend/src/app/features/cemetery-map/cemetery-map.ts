import { Component } from '@angular/core';

type PlotStatus = 'available' | 'occupied' | 'reserved';
type PlotFilter = 'all' | PlotStatus;

interface CemeteryPlot {
  id: string;
  row: number;
  column: number;
  status: PlotStatus;
}

interface ReservedArea {
  rowStart: number;
  rowEnd: number;
  columnStart: number;
  columnEnd: number;
}

interface CemeteryZone {
  id: string;
  name: string;
  rows: number;
  columns: number;
  cssClass: string;
  cells: Array<CemeteryPlot | null>;
  plotCount: number;
}

interface SelectedPlot {
  zone: CemeteryZone;
  plot: CemeteryPlot;
}

@Component({
  selector: 'app-cemetery-map',
  standalone: true,
  templateUrl: './cemetery-map.html',
  styleUrl: './cemetery-map.scss',
})
export class CemeteryMap {
  readonly currentDate = new Intl.DateTimeFormat('es-PE', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date());

  readonly currentTime = new Intl.DateTimeFormat('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date());

  readonly filterOptions: Array<{
    value: PlotFilter;
    label: string;
  }> = [
    {
      value: 'all',
      label: 'Todas',
    },
    {
      value: 'available',
      label: 'Disponibles',
    },
    {
      value: 'occupied',
      label: 'Ocupadas',
    },
    {
      value: 'reserved',
      label: 'Reservadas',
    },
  ];

  readonly zones: CemeteryZone[] = [
    this.createZone({
      id: 'A',
      name: 'Sector A',
      rows: 6,
      columns: 22,
      cssClass: 'zone--a',
      reservedAreas: [
        {
          rowStart: 1,
          rowEnd: 2,
          columnStart: 20,
          columnEnd: 22,
        },
      ],
    }),

    this.createZone({
      id: 'B',
      name: 'Sector B',
      rows: 6,
      columns: 22,
      cssClass: 'zone--b',
      reservedAreas: [
        {
          rowStart: 1,
          rowEnd: 2,
          columnStart: 20,
          columnEnd: 22,
        },
        {
          rowStart: 5,
          rowEnd: 6,
          columnStart: 1,
          columnEnd: 3,
        },
      ],
    }),

    this.createZone({
      id: 'C',
      name: 'Sector C',
      rows: 18,
      columns: 8,
      cssClass: 'zone--c',
      reservedAreas: [
        {
          rowStart: 1,
          rowEnd: 3,
          columnStart: 7,
          columnEnd: 8,
        },
        {
          rowStart: 16,
          rowEnd: 18,
          columnStart: 1,
          columnEnd: 2,
        },
      ],
    }),
  ];

  selectedPlot: SelectedPlot | null = null;
  activeFilter: PlotFilter = 'all';
  filterOpen = false;

  constructor() {
    const zoneC = this.zones.find((zone) => zone.id === 'C');

    const firstPlot = zoneC?.cells.find(
      (cell): cell is CemeteryPlot => cell !== null
    );

    if (zoneC && firstPlot) {
      this.selectedPlot = {
        zone: zoneC,
        plot: firstPlot,
      };
    }
  }

  get totalPlots(): number {
    return this.zones.reduce(
      (total, zone) => total + zone.plotCount,
      0
    );
  }

  get selectedStatusLabel(): string {
    if (!this.selectedPlot) {
      return '';
    }

    return this.getStatusLabel(this.selectedPlot.plot.status);
  }

  toggleFilters(): void {
    this.filterOpen = !this.filterOpen;
  }

  setFilter(filter: PlotFilter): void {
    this.activeFilter = filter;
    this.filterOpen = false;
  }

  selectPlot(zone: CemeteryZone, plot: CemeteryPlot): void {
    if (!this.matchesCurrentFilter(plot)) {
      return;
    }

    this.selectedPlot = {
      zone,
      plot,
    };
  }

  isSelected(zone: CemeteryZone, plot: CemeteryPlot): boolean {
    return (
      this.selectedPlot?.zone.id === zone.id &&
      this.selectedPlot?.plot.id === plot.id
    );
  }

  matchesCurrentFilter(plot: CemeteryPlot): boolean {
    return (
      this.activeFilter === 'all' ||
      plot.status === this.activeFilter
    );
  }

  getStatusLabel(status: PlotStatus): string {
    switch (status) {
      case 'available':
        return 'Disponible';

      case 'occupied':
        return 'Ocupada';

      case 'reserved':
        return 'Reservada';
    }
  }

  private createZone(config: {
    id: string;
    name: string;
    rows: number;
    columns: number;
    cssClass: string;
    reservedAreas: ReservedArea[];
  }): CemeteryZone {
    const cells: Array<CemeteryPlot | null> = [];
    let plotNumber = 0;

    for (let row = 1; row <= config.rows; row++) {
      for (let column = 1; column <= config.columns; column++) {
        const isReservedCell = config.reservedAreas.some(
          (area) =>
            row >= area.rowStart &&
            row <= area.rowEnd &&
            column >= area.columnStart &&
            column <= area.columnEnd
        );

        if (isReservedCell) {
          cells.push(null);
          continue;
        }

        plotNumber++;

        cells.push({
          id: `${config.id}-${plotNumber
            .toString()
            .padStart(3, '0')}`,
          row,
          column,
          status: this.generateStatus(plotNumber),
        });
      }
    }

    return {
      id: config.id,
      name: config.name,
      rows: config.rows,
      columns: config.columns,
      cssClass: config.cssClass,
      cells,
      plotCount: plotNumber,
    };
  }

  private generateStatus(plotNumber: number): PlotStatus {
    if (plotNumber % 17 === 0) {
      return 'reserved';
    }

    if (plotNumber % 7 === 0) {
      return 'occupied';
    }

    return 'available';
  }
}