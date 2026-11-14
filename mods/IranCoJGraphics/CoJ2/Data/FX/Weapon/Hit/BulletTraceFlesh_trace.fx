TraceDef()
{
	LifeTime()
	{
		keyf(0, 30)
	}

	Size()
	{
		randf(0, 5, 8)
	}

	MaxNumTraces(60)

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(22, 1, 1, 1, 1)
		keyv4(30, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_Wound_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
