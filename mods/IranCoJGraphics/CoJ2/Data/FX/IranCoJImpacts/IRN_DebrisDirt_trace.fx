TraceDef()
{
	LifeTime()
	{
		keyf(0, 8)
	}

	Size()
	{
		randf(0, 8, 14)
	}

	MaxNumTraces(200)

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(5, 1, 1, 1, 1)
		keyv4(8, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_DebrisDirt_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
