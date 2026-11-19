LONG_CHAT_COUNT = 12


class ListOrderStatements:
    def given_a_signed_in_person_with_two_chats_created_at_the_same_instant(self) -> None:
        self.given_a_signed_in_person()
        first_document = self._ready_pdf("same-instant-a.pdf")
        second_document = self._ready_pdf("same-instant-b.pdf")
        first = self.chats.create(self.token, first_document)
        second = self.chats.create(self.token, second_document)
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.body is not None
        assert second.body is not None
        self.same_instant_ids = [first.body["id"], second.body["id"]]
        self.first_list_order = None
        self.second_list_order = None

    def when_the_person_reads_the_chat_list_twice(self) -> None:
        first = self.chats.list(self.token)
        second = self.chats.list(self.token)
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.body is not None
        assert second.body is not None
        self.first_list_order = [row["id"] for row in first.body["chats"]]
        self.second_list_order = [row["id"] for row in second.body["chats"]]

    def then_the_two_chats_stay_in_the_same_order(self) -> None:
        assert self.first_list_order is not None
        assert self.second_list_order is not None
        pair_first = [chat_id for chat_id in self.first_list_order if chat_id in self.same_instant_ids]
        pair_second = [
            chat_id for chat_id in self.second_list_order if chat_id in self.same_instant_ids
        ]
        assert set(pair_first) == set(self.same_instant_ids)
        assert pair_first == pair_second
        assert self.first_list_order == self.second_list_order

    def given_a_signed_in_person_with_a_long_list_of_chats(self) -> None:
        self.given_a_signed_in_person()
        self.long_chat_ids = []
        for index in range(LONG_CHAT_COUNT):
            if index > 0:
                self.clock.advance(61)
            document_id = self._ready_pdf(f"long-list-{index:02d}.pdf")
            created = self.chats.create(self.token, document_id)
            assert created.status_code == 201
            assert created.body is not None
            self.long_chat_ids.append(created.body["id"])

    def when_the_person_reads_the_chat_list_counting_store_reads(self) -> None:
        reset = self.chats.reset_store_reads(self.token)
        assert reset.status_code == 204
        self.listed = self.chats.list(self.token)
        counted = self.chats.store_reads(self.token)
        assert counted.status_code == 200
        assert counted.body is not None
        self.store_reads = counted.body["reads"]

    def then_the_chat_store_is_read_a_constant_number_of_times(self) -> None:
        assert self.store_reads == 1

    def and_every_chat_this_person_owns_is_listed(self) -> None:
        listed = self.listed
        assert listed is not None
        assert listed.status_code == 200
        assert listed.body is not None
        ids = [row["id"] for row in listed.body["chats"]]
        assert set(ids) == set(self.long_chat_ids)
        assert len(ids) == LONG_CHAT_COUNT
