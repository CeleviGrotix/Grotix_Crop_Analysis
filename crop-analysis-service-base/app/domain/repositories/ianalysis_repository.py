from abc import ABC
from abc import abstractmethod


class IAnalysisRepository(ABC):

    @abstractmethod
    def save(self, report):
        pass

    @abstractmethod
    def find_latest_by_zone(self, zone_id):
        pass

    @abstractmethod
    def find_by_id(self, report_id):
        pass